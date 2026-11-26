"""One-time setup: AgentCore Gateway + web-search connector (us-east-1) for search.py.

Run this OUTSIDE the agent container with an ADMIN-capable AWS profile (the container's
profile is read-only and cannot create IAM roles or gateways):

  python setup_agentcore_gateway.py --profile <your-sso-admin-profile> \
      [--agent-principal-arn arn:aws:iam::<acct>:user-or-role/<the-agents-principal>]

What it does (idempotent — safe to re-run):
  1. Creates IAM role `gis-research-agentcore-gateway` (outbound: lets the Gateway call
     the managed web-search tool).
  2. Creates AgentCore Gateway `gis-research-search` (protocol MCP, inbound auth AWS_IAM).
  3. Attaches the `web-search` connector as a gateway target.
  4. Prints: the Gateway MCP URL (goes into ~/.config/gis-research.env as
     AGENTCORE_GATEWAY_URL) and the inbound-permission policy JSON to attach to the
     agents' principal (or attaches it directly if --agent-principal-arn names an IAM
     role/user you own and --attach is passed).

Cost: gateway itself is pay-per-use; web search = $7 per 1,000 queries.
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"  # web-search connector is us-east-1 only (2026-07)
ROLE_NAME = "gis-research-agentcore-gateway"
GATEWAY_NAME = "gis-research-search"
TOOL_ARN = f"arn:aws:bedrock-agentcore:{REGION}:aws:tool/web-search.v1"

TRUST = {
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
        "Action": "sts:AssumeRole",
    }],
}


def ensure_role(iam, account: str) -> str:
    try:
        arn = iam.get_role(RoleName=ROLE_NAME)["Role"]["Arn"]
        print(f"role exists: {arn}")
    except ClientError as e:
        if e.response["Error"]["Code"] != "NoSuchEntity":
            raise
        arn = iam.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(TRUST),
            Description="Outbound role for gis-research AgentCore search gateway",
        )["Role"]["Arn"]
        print(f"role created: {arn}")
        time.sleep(10)  # IAM propagation before the gateway tries to assume it
    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName="invoke-web-search",
        PolicyDocument=json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "InvokeWebSearch",
                "Effect": "Allow",
                "Action": "bedrock-agentcore:InvokeWebSearch",
                "Resource": TOOL_ARN,
            }],
        }),
    )
    return arn


def ensure_gateway(ctl, role_arn: str) -> dict:
    for g in ctl.list_gateways().get("items", []):
        if g["name"] == GATEWAY_NAME:
            print(f"gateway exists: {g['gatewayId']}")
            return ctl.get_gateway(gatewayIdentifier=g["gatewayId"])
    g = ctl.create_gateway(
        name=GATEWAY_NAME,
        description="gis-research agents: managed web search over MCP",
        roleArn=role_arn,
        protocolType="MCP",
        authorizerType="AWS_IAM",
    )
    print(f"gateway created: {g['gatewayId']} (status {g.get('status')})")
    while g.get("status") in ("CREATING",):
        time.sleep(5)
        g = ctl.get_gateway(gatewayIdentifier=g["gatewayId"])
    return g


def ensure_target(ctl, gateway_id: str) -> None:
    for t in ctl.list_gateway_targets(gatewayIdentifier=gateway_id).get("items", []):
        if t["name"] == "web-search-tool":
            print(f"target exists: {t['targetId']} (status {t.get('status')})")
            return
    t = ctl.create_gateway_target(
        gatewayIdentifier=gateway_id,
        name="web-search-tool",
        targetConfiguration={"mcp": {"connector": {
            "source": {"connectorId": "web-search"},
            "configurations": [{"name": "WebSearch", "parameterValues": {}}],
        }}},
        credentialProviderConfigurations=[{"credentialProviderType": "GATEWAY_IAM_ROLE"}],
    )
    print(f"target created: {t['targetId']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", required=True, help="admin-capable AWS profile")
    ap.add_argument("--agent-principal-arn", default=None,
                    help="IAM user/role the research agents run as (for inbound grant)")
    ap.add_argument("--attach", action="store_true",
                    help="attach the inbound policy to --agent-principal-arn (role/user)")
    a = ap.parse_args()

    s = boto3.Session(profile_name=a.profile, region_name=REGION)
    account = s.client("sts").get_caller_identity()["Account"]
    iam, ctl = s.client("iam"), s.client("bedrock-agentcore-control")

    role_arn = ensure_role(iam, account)
    g = ensure_gateway(ctl, role_arn)
    gateway_id, gateway_url = g["gatewayId"], g.get("gatewayUrl", "")
    ensure_target(ctl, gateway_id)

    gateway_arn = f"arn:aws:bedrock-agentcore:{REGION}:{account}:gateway/{gateway_id}"
    inbound = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "InvokeSearchGateway",
            "Effect": "Allow",
            "Action": "bedrock-agentcore:InvokeGateway",
            "Resource": gateway_arn,
        }],
    }
    if a.attach and a.agent_principal_arn:
        name = a.agent_principal_arn.split("/")[-1]
        kind = a.agent_principal_arn.split(":")[-1].split("/")[0]
        if kind == "role":
            iam.put_role_policy(RoleName=name, PolicyName="invoke-search-gateway",
                                PolicyDocument=json.dumps(inbound))
        else:
            iam.put_user_policy(UserName=name, PolicyName="invoke-search-gateway",
                                PolicyDocument=json.dumps(inbound))
        print(f"inbound policy attached to {a.agent_principal_arn}")
    else:
        print("\nattach this policy to the agents' IAM principal (inbound permission):")
        print(json.dumps(inbound, indent=2))

    print(f"\nGateway URL (put in ~/.config/gis-research.env):")
    print(f"AGENTCORE_GATEWAY_URL={gateway_url or f'https://{gateway_id}.gateway.bedrock-agentcore.{REGION}.amazonaws.com/mcp'}")
    print("\nthen test from the agent container:")
    print("  uv run gis-research/scripts/research_tools/search.py --selftest")


if __name__ == "__main__":
    sys.exit(main())
