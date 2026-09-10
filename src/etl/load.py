"""Load step: write output idempotently (an upsert keyed by customer_id).

Re-running the pipeline must not duplicate or corrupt data. We merge the new
batch into any existing output on customer_id, keeping the latest, then write a
deterministically-sorted file. Same inputs -> identical output file.
"""
from __future__ import annotations
import os
import pandas as pd


def load(df: pd.DataFrame, output_path: str) -> pd.DataFrame:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    if os.path.exists(output_path):
        existing = pd.read_csv(output_path)
        existing["customer_id"] = existing["customer_id"].astype(int)
        combined = pd.concat([existing, df], ignore_index=True)
        # upsert: last write wins for a given customer_id
        combined = combined.drop_duplicates(subset="customer_id", keep="last")
    else:
        combined = df.copy()

    combined = combined.sort_values("customer_id").reset_index(drop=True)
    combined.to_csv(output_path, index=False)
    return combined
