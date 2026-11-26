"""Real-time settlement-point LMPs from AW.DBO.SPTHRPRICEHOURLYVIEW.

Used for the LMP-pinning test: when a constraint is binding, the marginal
(curtailed) unit's node LMP should sit at its own DAM/RT offer price for the
dispatched segment while neighboring nodes and the hub diverge (their prices
move with the shadow price via -SF * shadow_price, the marginal unit's does
not once it is pinned against its own supply curve).

Schema note: SPTHRPRICEHOURLYVIEW carries one row per (CPNODEID, DATE, HE,
PRICETYPEID, PRICECOMPONENTID). As of 2026-08-12 the only PRICECOMPONENT
observed for ISOMARKETID=6 (ERCOT) settlement points is 1/"LMP" -- there is no
separate congestion-component row to difference against, so basis is computed
as node LMP minus a reference hub's LMP.
"""
from __future__ import annotations

import pandas as pd

from .. import sf

_COLUMNS = ["DATE", "HE", "CPNODEID", "DISPLAYNAME", "PRICE"]


def get_sp_prices(
    sp_names: list[str],
    start: str,
    end: str,
    price_type: int = 2,
    he: list[int] | None = None,
) -> pd.DataFrame:
    """Hourly LMPs for a list of settlement-point / CPNode display names.

    sp_names: exact DISPLAYNAME values (e.g. ["HB_WEST", "BOSQUESW_CC2"]).
      Case-sensitive match against SPTHRPRICEHOURLYVIEW.DISPLAYNAME.
    start/end: 'YYYY-MM-DD' bounds on DATE (inclusive start, exclusive end
      is NOT enforced here -- both bounds are inclusive via BETWEEN).
    price_type: PRICETYPEID (1=DA, 2=RT). Defaults to RT.
    he: optional list of hour-ending ints to restrict to (e.g. binding hours
      pulled from cong_history / CONGHRPRICE). None = all hours.

    Returns one row per (DISPLAYNAME, DATE, HE): DATE, HE, CPNODEID,
    DISPLAYNAME, PRICE. Empty frame (with columns) if sp_names is empty.
    """
    if not sp_names:
        return pd.DataFrame(columns=_COLUMNS)
    names = ",".join("'" + n.replace("'", "''") + "'" for n in sp_names)
    he_filter = ""
    if he:
        he_list = ",".join(str(int(h)) for h in he)
        he_filter = f"AND HE IN ({he_list})"
    sql = f"""
        SELECT DATE, HE, CPNODEID, DISPLAYNAME, PRICE
        FROM AW.DBO.SPTHRPRICEHOURLYVIEW
        WHERE DISPLAYNAME IN ({names})
          AND PRICETYPEID = {int(price_type)}
          AND DATE BETWEEN '{start}' AND '{end}'
          {he_filter}
        ORDER BY DISPLAYNAME, DATE, HE
    """
    df = sf.query("AW", sql)
    sf.validate_columns(df, _COLUMNS, "AW.DBO.SPTHRPRICEHOURLYVIEW")
    return df


def find_pinned_nodes(
    binding_hours: pd.DataFrame,
    candidate_prices: pd.DataFrame,
    hub_prices: pd.DataFrame,
    offers: dict[str, pd.DataFrame] | None = None,
    tol: float = 1.0,
) -> pd.DataFrame:
    """Flag candidate nodes whose LMP looks pinned relative to the hub, and
    (if offer curves are supplied) whether the pinned level matches a known
    offer segment.

    binding_hours: DataFrame with at least DATE, HE, PRICE (the constraint's
      shadow price) -- e.g. from cong_history's CONGHRPRICE pull.
    candidate_prices: output of get_sp_prices() for the candidate nodes.
    hub_prices: output of get_sp_prices() for a reference hub (e.g. HB_WEST).
    offers: optional {DISPLAYNAME: offer_curve_df} where offer_curve_df has a
      'PRICE'-like column of known offer segment prices (e.g. dam_bids
      get_offer_curve output) to check the pinned LMP against.
    tol: $/MWh tolerance for "pinned" (LMP within tol of an offer segment) and
      for treating the basis-vs-shadow-price fit as broken (i.e. some other
      constraint dominates that hour -- exclude rather than misread).

    Returns one row per (DATE, HE, DISPLAYNAME) with PRICE, HUB_PRICE, BASIS,
    and, if offers were supplied, the nearest offer price and whether it's
    within tol (PINNED bool).
    """
    merged = candidate_prices.merge(
        hub_prices[["DATE", "HE", "PRICE"]].rename(columns={"PRICE": "HUB_PRICE"}),
        on=["DATE", "HE"], how="left",
    )
    merged = merged.merge(
        binding_hours[["DATE", "HE"]].assign(_BINDING=True),
        on=["DATE", "HE"], how="left",
    )
    merged["_BINDING"] = merged["_BINDING"].fillna(False)
    merged["BASIS"] = merged["PRICE"] - merged["HUB_PRICE"]

    if offers:
        nearest_offer = []
        pinned = []
        for _, row in merged.iterrows():
            curve = offers.get(row["DISPLAYNAME"])
            if curve is None or curve.empty:
                nearest_offer.append(None)
                pinned.append(False)
                continue
            price_col = "PRICE" if "PRICE" in curve.columns else "MEDIAN_PRICE"
            diffs = (curve[price_col] - row["PRICE"]).abs()
            idx = diffs.idxmin()
            nearest_offer.append(curve.loc[idx, price_col])
            pinned.append(bool(diffs.loc[idx] <= tol))
        merged["NEAREST_OFFER_PRICE"] = nearest_offer
        merged["PINNED"] = pinned

    return merged
