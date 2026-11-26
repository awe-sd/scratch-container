def test_pipeline_package_importable(repo_root):
    import branch_tracking.pipeline  # noqa: F401
    assert (repo_root / "branch_tracking" / "pipeline" / "__init__.py").exists()
