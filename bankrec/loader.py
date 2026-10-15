"""Load bank statement and cash book exports into one standard layout.

Every bank and accounting system exports differently (column names, date
formats, "1,234.00" vs "1234"), so the column mapping lives in config.json.
After loading, both sources share the same columns:

    id, date, description, reference, voucher, amount

`amount` is signed from the company's point of view:
    +  money coming into the bank (deposit / cash book debit)
    -  money going out of the bank (withdrawal / cash book credit)
"""

import json
from pathlib import Path

import pandas as pd


def load_config(path):
    with open(path) as f:
        config = json.load(f)
    config["_base_dir"] = str(Path(path).resolve().parent)
    return config


def _to_amount(series):
    cleaned = series.astype(str).str.replace(",", "", regex=False).str.strip()
    return pd.to_numeric(cleaned.replace("", "0"), errors="coerce").fillna(0.0)


def load_source(path, mapping, prefix):
    """Read a CSV export and normalise it using a column mapping."""
    raw = pd.read_csv(path, dtype=str).fillna("")

    missing = [col for key, col in mapping.items()
               if key not in ("file", "date_format") and col not in raw.columns]
    if missing:
        raise ValueError(f"{path}: columns not found: {missing}")

    df = pd.DataFrame()
    # Row numbers match the spreadsheet (row 1 is the header) so items are easy to trace back.
    df["id"] = [f"{prefix}-{n}" for n in range(2, len(raw) + 2)]
    df["date"] = pd.to_datetime(raw[mapping["date"]].str.strip(), format=mapping.get("date_format"))
    df["description"] = raw[mapping["description"]].str.strip()
    df["reference"] = raw[mapping["reference"]].str.strip().str.upper() if "reference" in mapping else ""
    df["voucher"] = raw[mapping["voucher"]].str.strip() if "voucher" in mapping else ""
    df["amount"] = (_to_amount(raw[mapping["inflow"]]) - _to_amount(raw[mapping["outflow"]])).round(2)
    if "balance" in mapping:
        df["balance"] = _to_amount(raw[mapping["balance"]]).round(2)
    return df.set_index("id", drop=False)


def closing_balance(df, opening):
    """Closing balance = opening + net movement.

    If the export carries a running balance, also check it agrees with the
    transactions - a quick integrity check that no rows were lost in the export.
    """
    computed = round(opening + df["amount"].sum(), 2)
    if "balance" in df.columns and len(df):
        reported = round(df["balance"].iloc[-1], 2)
        if abs(reported - computed) > 0.005:
            raise ValueError(
                f"Statement integrity check failed: running balance shows {reported:,.2f} "
                f"but opening + transactions = {computed:,.2f}. Check the export for missing rows."
            )
    return computed
