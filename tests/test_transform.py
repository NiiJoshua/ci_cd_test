"""Unit tests for deterministic transforms."""
import pandas as pd
from src.etl.validate import validate
from src.etl.transform import transform


def test_transform_normalises_email_and_country():
    df = pd.DataFrame(
        [{"customer_id": "5", "email": " A@B.COM ", "country": "gh", "signup_date": "2025-01-01"}],
        dtype=str,
    )
    clean, _, _ = validate(df)
    out = transform(clean)
    row = out.iloc[0]
    assert row["email"] == "a@b.com"
    assert row["country"] == "GH"
    assert row["signup_year"] == 2025
    assert row["customer_id"] == 5  # coerced to int


def test_transform_is_deterministic():
    df = pd.DataFrame(
        [
            {"customer_id": "3", "email": "c@x.com", "country": "RW", "signup_date": "2025-03-03"},
            {"customer_id": "1", "email": "a@x.com", "country": "GH", "signup_date": "2025-01-01"},
        ],
        dtype=str,
    )
    clean, _, _ = validate(df)
    out1 = transform(clean)
    out2 = transform(clean)
    pd.testing.assert_frame_equal(out1, out2)
    # sorted by id regardless of input order
    assert list(out1["customer_id"]) == [1, 3]
