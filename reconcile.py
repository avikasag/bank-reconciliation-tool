"""Run a bank reconciliation from the command line.

    python reconcile.py                      # uses config.json and the sample data
    python reconcile.py --config my.json --output reports/
"""

import argparse
from pathlib import Path

import pandas as pd

from bankrec import build_statement, classify, closing_balance, journal_entries, load_config, load_source, reconcile
from bankrec.report import print_summary, write_excel, write_markdown


def main():
    parser = argparse.ArgumentParser(description="Reconcile a bank statement against the cash book.")
    parser.add_argument("--config", default="config.json", help="path to the config file")
    parser.add_argument("--output", default="output", help="folder for the reconciliation pack")
    args = parser.parse_args()

    config = load_config(args.config)
    base = Path(config["_base_dir"])
    bank = load_source(base / config["bank"]["file"], config["bank"], "BANK")
    books = load_source(base / config["books"]["file"], config["books"], "BOOK")

    bank_balance = closing_balance(bank, config["opening_balance_per_bank"])
    book_balance = closing_balance(books, config["opening_balance_per_books"])

    results = reconcile(bank, books, config.get("date_tolerance_days", 5))
    bank_side, book_side = classify(results, config["period_end"], config.get("stale_item_days", 90))
    statement = build_statement(bank_balance, book_balance, bank_side, book_side)
    journals = journal_entries(book_side, config["bank_ledger_name"])

    matched = results["matched"]
    counts = {
        "Bank statement lines": len(bank),
        "Cash book entries": len(books),
        "Matched on reference + amount": int((matched["match_type"] == "Reference + amount").sum()),
        "Matched on amount + date": int((matched["match_type"] != "Reference + amount").sum()),
        "Amount mismatches": len(results["amount_mismatches"]),
        "Duplicate entries": len(results["duplicate_books"]) + len(results["duplicate_bank"]),
        "Timing differences": len(bank_side),
        "Book adjustments required": len(book_side),
    }

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = pd.Timestamp(config["period_end"]).strftime("%Y-%m")
    excel_path = out_dir / f"bank_reconciliation_{stamp}.xlsx"
    md_path = out_dir / f"bank_reconciliation_{stamp}.md"
    write_excel(excel_path, config, results, bank_side, book_side, statement, journals, counts)
    write_markdown(md_path, config, bank_side, book_side, statement, journals, counts)

    print_summary(config, statement, counts)
    print(f"\nReports written to:\n  {excel_path}\n  {md_path}")


if __name__ == "__main__":
    main()
