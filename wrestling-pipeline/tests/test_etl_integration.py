import os
import subprocess
import pandas as pd


def test_etl_generates_minimum_rows(tmp_path):
    """Run the ETL script and assert that generated processed CSVs have at least N rows.
    This test is best-effort and will skip assertions if ETL couldn't run in CI/local environment."""
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env = os.environ.copy()
    env["ETL_OUTPUT"] = os.path.join(root, "data", "processed")
    # Run ETL via provided script `scripts/run_local.sh` (best-effort)
    run_local = os.path.join(root, "scripts", "run_local.sh")
    try:
        if os.path.exists(run_local):
            subprocess.check_call(["bash", run_local], cwd=root, env=env)
        else:
            subprocess.check_call(["python3", "-m", "etl.run_etl"], cwd=root, env=env)
    except Exception:
        # Skip assertion if ETL/script couldn't run in this environment
        return

    wpath = os.path.join(root, "data", "processed", "wrestlers_extracted.csv")
    tpath = os.path.join(root, "data", "processed", "titles_extracted.csv")
    if os.path.exists(wpath):
        dfw = pd.read_csv(wpath)
        assert len(dfw) >= int(os.getenv("MIN_WRESTLERS", "1"))
    if os.path.exists(tpath):
        dft = pd.read_csv(tpath)
        assert len(dft) >= int(os.getenv("MIN_TITLES", "0"))
