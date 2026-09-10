"""Integration test for idempotency & safe re-runs — the 'coverage' end of the
speed/coverage trade-off. Slower: it does real file I/O end to end.

Marked 'integration' so CI can run it in a separate, slower stage if desired:
    pytest -m "not integration"   # fast feedback
    pytest                         # everything
"""
import hashlib
import pytest
from src.etl.pipeline import run

RAW = "data/raw/customers_raw.csv"


def _sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


@pytest.mark.integration
def test_running_twice_is_idempotent(tmp_path):
    out = tmp_path / "customers_clean.csv"

    r1 = run(RAW, str(out))
    hash1 = _sha256(out)
    rows1 = r1["rows_written"]

    # re-run on the SAME input: must not duplicate rows or change the file
    r2 = run(RAW, str(out))
    hash2 = _sha256(out)
    rows2 = r2["rows_written"]

    assert rows1 == rows2, "row count changed on re-run — not idempotent"
    assert hash1 == hash2, "output file changed on re-run — not idempotent"


@pytest.mark.integration
def test_pipeline_rejects_bad_rows(tmp_path):
    out = tmp_path / "out.csv"
    report = run("data/raw/customers_bad.csv", str(out), fail_on_reject=True)
    assert report["rows_rejected"] >= 4
    assert report["failed"] is True
