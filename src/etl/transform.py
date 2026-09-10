"""Transform step: normalise columns deterministically.

Determinism matters: the same input must always yield the same output, or the
idempotency test (and safe re-runs) will fail.
"""
from __future__ import annotations
import pandas as pd


def transform(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out

    out["customer_id"] = out["customer_id"].astype(int)
    out["email"] = out["email"].str.strip().str.lower()
    out["country"] = out["country"].str.strip().str.upper()
    out["signup_date"] = pd.to_datetime(out["signup_date"], format="%Y-%m-%d").dt.date
    out["signup_year"] = pd.to_datetime(out["signup_date"]).dt.year

    keep = ["customer_id", "email", "country", "signup_date", "signup_year"]
    keep = [c for c in keep if c in out.columns]
    out = out[keep]

    # a stable sort makes the written output byte-for-byte reproducible
    out = out.sort_values("customer_id").reset_index(drop=True)
    return out
