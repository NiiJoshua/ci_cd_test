"""Extract step: read raw data into a DataFrame."""
from __future__ import annotations
import pandas as pd


def extract(input_path: str) -> pd.DataFrame:
    """Read the raw CSV. Kept deliberately simple: one source, one function.

    Reading is side-effect free, which is what lets the whole pipeline be
    idempotent — running it again reads the same bytes and produces the same
    frame.
    """
    df = pd.read_csv(input_path, dtype=str)  # read as str; we coerce types in validate
    return df
