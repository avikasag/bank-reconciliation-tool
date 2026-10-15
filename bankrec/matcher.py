"""Match bank statement lines to cash book entries.

Matching runs in passes, strictest first, and each line can be used once:

  1. Duplicates   - the same entry posted twice in one source is set aside
  2. Exact        - same reference and same amount
  3. Mismatch     - same reference, same direction, different amount
                    (usually a posting error, e.g. 7,250 keyed instead of 7,520)
  4. Amount+date  - no common reference, but same amount within N days
                    (bank narrations often carry their own reference numbers)

Whatever is left over is unmatched and gets classified in classifier.py.
"""

import pandas as pd

AMOUNT_TOLERANCE = 0.005


def find_duplicates(df):
    """Split off entries that repeat an earlier one (same date, amount and reference).

    When there is no reference the description is used instead. The first
    occurrence is kept for matching; the repeats are returned separately.
    """
    key = df["reference"].where(df["reference"] != "", df["description"].str.upper())
    dup_mask = pd.DataFrame({"d": df["date"], "a": df["amount"], "k": key}).duplicated(keep="first")
    return df[~dup_mask], df[dup_mask]


def _match_pass(bank, books, used_bank, used_books, condition, match_type):
    pairs = []
    for book_id, book in books.iterrows():
        if book_id in used_books:
            continue
        candidates = bank[~bank.index.isin(used_bank)]
        candidates = candidates[condition(candidates, book)]
        if candidates.empty:
            continue
        # If several bank lines qualify, take the one closest in date.
        bank_id = (candidates["date"] - book["date"]).abs().idxmin()
        bank_line = bank.loc[bank_id]
        used_bank.add(bank_id)
        used_books.add(book_id)
        pairs.append({
            "match_type": match_type,
            "book_id": book_id,
            "bank_id": bank_id,
            "voucher": book["voucher"],
            "book_date": book["date"],
            "bank_date": bank_line["date"],
            "days_apart": (bank_line["date"] - book["date"]).days,
            "book_reference": book["reference"],
            "bank_reference": bank_line["reference"],
            "description": book["description"],
            "book_amount": book["amount"],
            "bank_amount": bank_line["amount"],
            "difference": round(bank_line["amount"] - book["amount"], 2),
        })
    return pairs


def reconcile(bank, books, date_tolerance_days=5):
    """Run all matching passes. Returns a dict of DataFrames."""
    bank, bank_dups = find_duplicates(bank)
    books, book_dups = find_duplicates(books)
    used_bank, used_books = set(), set()

    def same_amount(c, b):
        return (c["amount"] - b["amount"]).abs() < AMOUNT_TOLERANCE

    def same_reference(c, b):
        return (b["reference"] != "") & (c["reference"] == b["reference"])

    def same_direction(c, b):
        return (c["amount"] > 0) == (b["amount"] > 0)

    def within_days(c, b):
        return (c["date"] - b["date"]).abs().dt.days <= date_tolerance_days

    exact = _match_pass(bank, books, used_bank, used_books,
                        lambda c, b: same_reference(c, b) & same_amount(c, b),
                        "Reference + amount")
    mismatched = _match_pass(bank, books, used_bank, used_books,
                             lambda c, b: same_reference(c, b) & same_direction(c, b) & ~same_amount(c, b),
                             "Reference only - amount differs")
    by_amount = _match_pass(bank, books, used_bank, used_books,
                            lambda c, b: same_amount(c, b) & within_days(c, b),
                            f"Amount + date (within {date_tolerance_days} days)")

    columns = ["match_type", "book_id", "bank_id", "voucher", "book_date", "bank_date", "days_apart",
               "book_reference", "bank_reference", "description", "book_amount", "bank_amount", "difference"]
    return {
        "matched": pd.DataFrame(exact + by_amount, columns=columns),
        "amount_mismatches": pd.DataFrame(mismatched, columns=columns),
        "unmatched_bank": bank[~bank.index.isin(used_bank)].copy(),
        "unmatched_books": books[~books.index.isin(used_books)].copy(),
        "duplicate_bank": bank_dups.copy(),
        "duplicate_books": book_dups.copy(),
    }
