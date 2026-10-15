"""Build the bank reconciliation statement and the adjusting journal entries.

Uses the "adjusted balance" method - both balances are brought to the true
cash figure independently, and they must agree:

    Balance per bank statement            Balance per cash book
  + Deposits in transit                 + Bank credits not yet recorded
  - Outstanding cheques / payments      - Bank debits not yet recorded
                                        +/- Error corrections
  = Adjusted bank balance               = Adjusted book balance
"""

import pandas as pd


def _category_lines(items):
    """One line per category, additions first then deductions (standard BRS layout)."""
    totals = items.groupby("category", sort=False)["adjustment"].sum()
    adds = [(f"Add: {cat}", amt, "item") for cat, amt in totals.items() if amt > 0]
    less = [(f"Less: {cat}", amt, "item") for cat, amt in totals.items() if amt <= 0]
    return adds + less


def build_statement(bank_balance, book_balance, bank_side, book_side):
    """Return the statement as an ordered list of (label, amount, kind) lines plus totals."""
    lines = [("Balance as per bank statement", bank_balance, "balance")]
    lines += _category_lines(bank_side)
    adjusted_bank = round(bank_balance + bank_side["adjustment"].sum(), 2)
    lines.append(("Adjusted bank balance", adjusted_bank, "total"))

    lines.append(("Balance as per cash book", book_balance, "balance"))
    lines += _category_lines(book_side)
    adjusted_book = round(book_balance + book_side["adjustment"].sum(), 2)
    lines.append(("Adjusted book balance", adjusted_book, "total"))

    difference = round(adjusted_bank - adjusted_book, 2)
    lines.append(("Unexplained difference", difference, "check"))
    return {
        "lines": lines,
        "adjusted_bank": adjusted_bank,
        "adjusted_book": adjusted_book,
        "difference": difference,
        "reconciled": abs(difference) < 0.01,
    }


def journal_entries(book_side, bank_ledger):
    """Suggested adjusting entries so the cash book agrees with the bank.

    Money in  (adjustment > 0): Dr Bank, Cr contra account
    Money out (adjustment < 0): Dr contra account, Cr Bank
    """
    rows = []
    for n, item in enumerate(book_side.itertuples(), start=1):
        amount = round(abs(item.adjustment), 2)
        debit, credit = (bank_ledger, item.contra_account) if item.adjustment > 0 else (item.contra_account, bank_ledger)
        narration = f"{item.category}: {item.description} ({item.reference})"
        rows.append([f"JE-{n:02d}", item.date, debit, amount, None, narration])
        rows.append([f"JE-{n:02d}", item.date, f"    To {credit}", None, amount, ""])
    return pd.DataFrame(rows, columns=["entry", "date", "account", "debit", "credit", "narration"])
