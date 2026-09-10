"""Validate step: enforce a small data contract and split good vs. bad rows.

This is the 'C' quality gate that CI will run automatically on every push.
"""
from __future__ import annotations
import re
import pandas as pd

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_COUNTRIES = {"GH", "RW", "SN", "NG", "CI"}
REQUIRED_COLUMNS = ["customer_id", "email", "country", "signup_date"]


def _row_errors(row: pd.Series) -> list[str]:
    errors: list[str] = []

    # required columns present and non-empty
    for col in REQUIRED_COLUMNS:
        val = row.get(col)
        if val is None or (isinstance(val, float) and pd.isna(val)) or str(val).strip() == "":
            errors.append(f"{col}: missing")

    # customer_id must be an integer
    cid = str(row.get("customer_id", "")).strip()
    if cid and not cid.isdigit():
        errors.append("customer_id: not an integer")

    # email format
    email = str(row.get("email", "")).strip()
    if email and not EMAIL_RE.match(email):
        errors.append("email: bad format")

    # country in allowed set
    country = str(row.get("country", "")).strip().upper()
    if country and country not in ALLOWED_COUNTRIES:
        errors.append(f"country: '{country}' not allowed")

    # signup_date parseable as a real date
    sd = str(row.get("signup_date", "")).strip()
    if sd:
        parsed = pd.to_datetime(sd, errors="coerce", format="%Y-%m-%d")
        if pd.isna(parsed):
            errors.append("signup_date: unparseable (want YYYY-MM-DD)")

    return errors


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Return (clean_df, rejects_df, report).

    clean_df  — rows that satisfy the contract (deduplicated by customer_id)
    rejects_df— rows that failed, with a 'errors' column explaining why
    report    — small dict summarising the run (handy for CI logs)
    """
    if df.empty:
        return df.copy(), df.copy(), {"rows_in": 0, "rows_clean": 0, "rows_rejected": 0}

    error_lists = df.apply(_row_errors, axis=1)
    is_valid = error_lists.map(len) == 0

    clean = df[is_valid].copy()
    rejects = df[~is_valid].copy()
    rejects["errors"] = error_lists[~is_valid].map("; ".join)

    # uniqueness is a contract rule too: keep the last occurrence of each id
    dupes = clean["customer_id"].duplicated(keep="last")
    if dupes.any():
        moved = clean[dupes].copy()
        moved["errors"] = "customer_id: duplicate"
        rejects = pd.concat([rejects, moved], ignore_index=True)
        clean = clean[~dupes].copy()

    report = {
        "rows_in": int(len(df)),
        "rows_clean": int(len(clean)),
        "rows_rejected": int(len(rejects)),
    }
    return clean.reset_index(drop=True), rejects.reset_index(drop=True), report
