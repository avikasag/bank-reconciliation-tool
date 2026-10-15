from pathlib import Path

import pandas as pd
import pytest

from bankrec import build_statement, classify, closing_balance, journal_entries, load_config, load_source, reconcile

ROOT = Path(__file__).resolve().parents[1]


def make(rows, prefix):
    df = pd.DataFrame(rows, columns=["date", "description", "reference", "amount"])
    df["date"] = pd.to_datetime(df["date"])
    df["voucher"] = ""
    df["id"] = [f"{prefix}-{i}" for i in range(len(df))]
    return df.set_index("id", drop=False)


def test_exact_match_on_reference_and_amount():
    bank = make([("2026-09-05", "CHQ PAID", "100231", -45000.0)], "BANK")
    books = make([("2026-09-03", "Rent", "100231", -45000.0)], "BOOK")
    r = reconcile(bank, books)
    assert len(r["matched"]) == 1
    assert r["matched"].iloc[0]["match_type"] == "Reference + amount"
    assert r["unmatched_bank"].empty and r["unmatched_books"].empty


def test_amount_and_date_match_when_references_differ():
    bank = make([("2026-09-15", "NEFT DR", "N258261234", -12600.0)], "BANK")
    books = make([("2026-09-14", "Freight", "NEFT-PO2207", -12600.0)], "BOOK")
    r = reconcile(bank, books, date_tolerance_days=5)
    assert r["matched"].iloc[0]["match_type"].startswith("Amount + date")


def test_amount_match_outside_tolerance_is_not_matched():
    bank = make([("2026-09-25", "NEFT DR", "X1", -12600.0)], "BANK")
    books = make([("2026-09-01", "Freight", "Y1", -12600.0)], "BOOK")
    r = reconcile(bank, books, date_tolerance_days=5)
    assert r["matched"].empty


def test_same_reference_different_amount_is_flagged_as_mismatch():
    bank = make([("2026-09-19", "CHQ PAID", "100234", -7520.0)], "BANK")
    books = make([("2026-09-17", "Verma Packaging", "100234", -7250.0)], "BOOK")
    r = reconcile(bank, books)
    assert len(r["amount_mismatches"]) == 1
    assert r["amount_mismatches"].iloc[0]["difference"] == -270.0


def test_duplicate_posting_is_detected():
    books = make([("2026-09-21", "Internet", "ISP-SEP26", -2360.0),
                  ("2026-09-21", "Internet", "ISP-SEP26", -2360.0)], "BOOK")
    bank = make([("2026-09-21", "BILLPAY", "ISP-SEP26", -2360.0)], "BANK")
    r = reconcile(bank, books)
    assert len(r["matched"]) == 1
    assert len(r["duplicate_books"]) == 1


def test_classification_of_unmatched_items():
    bank = make([("2026-09-30", "ACCOUNT MAINTENANCE CHARGES", "CHG-1", -590.0),
                 ("2026-09-30", "INTEREST CREDITED", "INT-CR-1", 1245.0),
                 ("2026-09-26", "CHQ RETURNED-INSUFFICIENT FUNDS", "RTN-1", -40000.0)], "BANK")
    books = make([("2026-09-28", "Paid supplier", "100235", -15400.0),
                  ("2026-09-30", "Cheque deposited", "DEP-5530", 36500.0)], "BOOK")
    bank_side, book_side = classify(reconcile(bank, books), "2026-09-30")
    assert set(bank_side["category"]) == {"Outstanding cheque (issued, not presented)", "Deposit in transit"}
    assert set(book_side["category"]) == {"Bank charges", "Interest credited by bank", "Dishonoured cheque"}


def test_statement_integrity_check_catches_missing_rows():
    bank = make([("2026-09-01", "X", "A", 100.0)], "BANK")
    bank["balance"] = [999.0]
    with pytest.raises(ValueError, match="integrity"):
        closing_balance(bank, 0)


def test_sample_data_reconciles_end_to_end():
    config = load_config(ROOT / "config.json")
    bank = load_source(ROOT / config["bank"]["file"], config["bank"], "BANK")
    books = load_source(ROOT / config["books"]["file"], config["books"], "BOOK")
    results = reconcile(bank, books, config["date_tolerance_days"])
    bank_side, book_side = classify(results, config["period_end"])
    statement = build_statement(closing_balance(bank, 250000), closing_balance(books, 250000), bank_side, book_side)

    assert statement["reconciled"]
    assert statement["adjusted_bank"] == statement["adjusted_book"] == 178100.0

    journals = journal_entries(book_side, config["bank_ledger_name"])
    assert journals["debit"].sum() == pytest.approx(journals["credit"].sum())
