"""Explain every item that did not match.

Unmatched items fall into two groups, and the split decides which side of the
reconciliation statement they go on:

  Bank side (timing differences - no entry needed, they clear next month)
    - Deposits in transit: in the books, not yet credited by the bank
    - Outstanding payments: cheques issued / payments made, not yet presented
    - Duplicate lines on the bank statement: bank error, raise with the bank

  Book side (adjustments - the cash book must be corrected with a journal)
    - Bank charges, interest, direct debits/credits, dishonoured cheques
    - Amount mismatches (posting errors)
    - Duplicate postings in the cash book
"""

import re

import pandas as pd

# Checked in order; first match wins. Charges come before returns so that
# "CHQ RETURN CHARGES" is treated as a charge, not as the returned cheque itself.
BANK_ONLY_RULES = [
    (r"CHARGE|CHG|\bFEE\b|COMMISSION", "Bank charges", "Bank Charges (expense)"),
    (r"RETURN|RTN|BOUNCE|DISHONOU?R|INSUFFICIENT", "Dishonoured cheque",
     "Accounts Receivable - reinstate customer balance"),
    (r"INTEREST|INT[- ]?CR", "Interest credited by bank", "Interest Income"),
    (r"NACH|ECS|AUTO ?DEBIT|STANDING INSTRUCTION", "Direct debit (NACH/ECS)",
     "Loan / expense as per mandate - verify"),
]

BANK_SIDE_COLUMNS = ["date", "ref_id", "description", "reference", "category", "adjustment", "age_days", "note"]
BOOK_SIDE_COLUMNS = ["date", "ref_id", "description", "reference", "category", "adjustment", "contra_account"]


def _classify_bank_only(row):
    text = f"{row['description']} {row['reference']}".upper()
    for pattern, category, contra in BANK_ONLY_RULES:
        if re.search(pattern, text):
            return category, contra
    if row["amount"] > 0:
        return "Direct credit not recorded in books", "Suspense - identify customer / receipt"
    return "Direct debit not recorded in books", "Suspense - investigate payment"


def classify(results, period_end, stale_days=90):
    """Return (bank_side, book_side) DataFrames of reconciling items.

    `adjustment` is the signed amount to add to that side's balance.
    """
    period_end = pd.Timestamp(period_end)
    bank_side, book_side = [], []

    for book_id, row in results["unmatched_books"].iterrows():
        age = (period_end - row["date"]).days
        if row["amount"] > 0:
            category = "Deposit in transit"
        elif row["reference"].isdigit():
            category = "Outstanding cheque (issued, not presented)"
        else:
            category = "Outstanding payment (not yet cleared)"
        note = f"Stale - over {stale_days} days, investigate" if age > stale_days else "Should clear next month"
        bank_side.append([row["date"], row["voucher"] or book_id, row["description"], row["reference"],
                          category, row["amount"], age, note])

    for bank_id, row in results["duplicate_bank"].iterrows():
        bank_side.append([row["date"], bank_id, row["description"], row["reference"],
                          "Duplicate on bank statement", -row["amount"], (period_end - row["date"]).days,
                          "Bank error - raise with the bank"])

    for bank_id, row in results["unmatched_bank"].iterrows():
        category, contra = _classify_bank_only(row)
        book_side.append([row["date"], bank_id, row["description"], row["reference"],
                          category, row["amount"], contra])

    for _, m in results["amount_mismatches"].iterrows():
        book_side.append([m["book_date"], m["voucher"] or m["book_id"],
                          f"{m['description']} (books {abs(m['book_amount']):,.2f} vs bank {abs(m['bank_amount']):,.2f})",
                          m["book_reference"], "Posting error - amount mismatch", m["difference"],
                          f"Original ledger of {m['voucher']} - correct the amount"])

    for book_id, row in results["duplicate_books"].iterrows():
        book_side.append([row["date"], row["voucher"] or book_id, row["description"], row["reference"],
                          "Duplicate posting in cash book", -row["amount"],
                          f"Original ledger of {row['voucher']} - reverse duplicate voucher"])

    bank_df = pd.DataFrame(bank_side, columns=BANK_SIDE_COLUMNS).sort_values("date", kind="stable")
    book_df = pd.DataFrame(book_side, columns=BOOK_SIDE_COLUMNS).sort_values("date", kind="stable")
    return bank_df.reset_index(drop=True), book_df.reset_index(drop=True)
