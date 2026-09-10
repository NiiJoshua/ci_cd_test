"""Fast unit tests for the data contract — the 'speed' end of the trade-off."""
import pandas as pd
from src.etl.validate import validate


def _df(rows):
    return pd.DataFrame(rows, dtype=str)


def test_all_good_rows_pass():
    df = _df([
        {"customer_id": "1", "email": "a@b.com", "country": "GH", "signup_date": "2025-01-01"},
        {"customer_id": "2", "email": "c@d.com", "country": "RW", "signup_date": "2025-02-02"},
    ])
    clean, rejects, report = validate(df)
    assert report["rows_clean"] == 2
    assert report["rows_rejected"] == 0
    assert rejects.empty


def test_bad_email_is_rejected():
    df = _df([{"customer_id": "1", "email": "nope", "country": "GH", "signup_date": "2025-01-01"}])
    clean, rejects, _ = validate(df)
    assert clean.empty
    assert "email: bad format" in rejects.iloc[0]["errors"]


def test_disallowed_country_is_rejected():
    df = _df([{"customer_id": "1", "email": "a@b.com", "country": "ZZ", "signup_date": "2025-01-01"}])
    _, rejects, _ = validate(df)
    assert "not allowed" in rejects.iloc[0]["errors"]


def test_non_integer_id_is_rejected():
    df = _df([{"customer_id": "12X", "email": "a@b.com", "country": "GH", "signup_date": "2025-01-01"}])
    _, rejects, _ = validate(df)
    assert "customer_id: not an integer" in rejects.iloc[0]["errors"]


def test_missing_required_field_is_rejected():
    df = _df([{"customer_id": "1", "email": "a@b.com", "country": "", "signup_date": "2025-01-01"}])
    _, rejects, _ = validate(df)
    assert "country: missing" in rejects.iloc[0]["errors"]


def test_duplicate_id_kept_once():
    df = _df([
        {"customer_id": "1", "email": "a@b.com", "country": "GH", "signup_date": "2025-01-01"},
        {"customer_id": "1", "email": "a@b.com", "country": "GH", "signup_date": "2025-01-02"},
    ])
    clean, rejects, report = validate(df)
    assert report["rows_clean"] == 1
    assert (rejects["errors"] == "customer_id: duplicate").any()
