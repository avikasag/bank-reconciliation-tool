# Automated Bank Reconciliation Tool

A Python tool that reconciles a bank statement against the cash book (bank ledger) at month end. It matches transactions automatically, explains every item that doesn't match, and produces a ready-to-review **Bank Reconciliation Statement (BRS)** with the **adjusting journal entries** needed to correct the books.

Manual bank reconciliation in Excel means ticking off hundreds of lines by eye. This tool does the matching in seconds and leaves the accountant to review only the exceptions.

---

## What it does

| Step | What happens |
|---|---|
| **1. Load and normalise** | Reads CSV exports from any bank or accounting system. Column names, date formats and `1,234.00`-style amounts are handled through `config.json`. |
| **2. Integrity check** | Confirms the bank statement's running balance agrees with opening balance + transactions, so a broken or partial export is caught before reconciling. |
| **3. Duplicate detection** | Flags entries posted twice (same date, amount and reference) in either source. |
| **4. Matching** | Pairs bank lines with cash book entries in passes, strictest first:<br>• **Reference + amount**: cheque no., UTR or invoice ref and amount agree<br>• **Reference only, amount differs**: flagged as a posting error (e.g. 7,250 keyed instead of 7,520)<br>• **Amount + date within N days**: for electronic payments where the bank uses its own reference |
| **5. Classification** | Every unmatched item is categorised:<br>• **Timing differences** (bank side): deposits in transit, outstanding cheques, stale items over 90 days<br>• **Book adjustments** (book side): bank charges, interest, NACH/ECS debits, dishonoured cheques, unrecorded direct credits, posting errors, duplicates |
| **6. BRS + journals** | Builds the reconciliation statement using the adjusted-balance method, checks that the unexplained difference is zero, and suggests the journal entries to pass. |

## Sample result

The sample data (`data/`) covers one month (September 2026) for a fictional company. It includes the issues a real reconciliation runs into: outstanding cheques, a deposit in transit, a bounced cheque, bank charges, interest, a loan EMI by NACH, an unidentified customer receipt, a transposition error and a duplicate voucher.

```
==============================================================
Sharma Traders Pvt Ltd - Bank Reconciliation
As at 30 September 2026 (INR)
==============================================================

Balance as per bank statement                         179,000.00
  Add: Deposit in transit                              36,500.00
  Less: Outstanding cheque (issued, not presented)   (37,400.00)
Adjusted bank balance                                 178,100.00
--------------------------------------------------------------

Balance as per cash book                              206,209.00
  Add: Duplicate posting in cash book                   2,360.00
  Add: Direct credit not recorded in books             28,000.00
  Add: Interest credited by bank                        1,245.00
  Less: Direct debit (NACH/ECS)                      (18,500.00)
  Less: Posting error - amount mismatch                 (270.00)
  Less: Dishonoured cheque                           (40,000.00)
  Less: Bank charges                                    (944.00)
Adjusted book balance                                 178,100.00
--------------------------------------------------------------
Unexplained difference                                      0.00

STATUS: RECONCILED
```

20 bank lines and 18 cash book entries: **13 matched automatically**, 1 amount mismatch, 1 duplicate, 3 timing differences and 8 book adjustments, all explained.

Full output: [`output/bank_reconciliation_2026-09.md`](output/bank_reconciliation_2026-09.md) and the Excel pack [`output/bank_reconciliation_2026-09.xlsx`](output/bank_reconciliation_2026-09.xlsx).

### Excel reconciliation pack

| Sheet | Contents |
|---|---|
| Reconciliation | The formatted BRS with status (green when reconciled) and matching summary |
| Matched | Every matched pair with match type, dates and days apart |
| Timing Differences | Deposits in transit and outstanding cheques with ageing |
| Book Adjustments | Items to record in the books, with the suggested contra account |
| Journal Entries | Balanced Dr/Cr adjusting entries, ready to post |
| Unmatched - Bank / Books | Raw unmatched lines for audit trail |

## How to run

```bash
git clone https://github.com/<your-username>/bank-reconciliation-tool.git
cd bank-reconciliation-tool
pip install -r requirements.txt
python reconcile.py
```

Reports are written to `output/`. Run the tests with `pytest`.

### Using your own data

Export the bank statement and the bank ledger as CSV, then edit `config.json`:

```json
"bank": {
  "file": "data/my_bank_statement.csv",
  "date": "Txn Date",          "date_format": "%d-%m-%Y",
  "description": "Narration",  "reference": "Ref No",
  "inflow": "Deposit",         "outflow": "Withdrawal",
  "balance": "Balance"
}
```

Also set the opening balances, the period end date and the matching tolerance (`date_tolerance_days`). Then run `python reconcile.py --config config.json --output output/`.

## Project structure

```
bank-reconciliation-tool/
├── reconcile.py          # command-line entry point
├── config.json           # column mapping, balances, tolerances
├── bankrec/
│   ├── loader.py         # read and normalise CSVs, balance integrity check
│   ├── matcher.py        # duplicate detection + multi-pass matching
│   ├── classifier.py     # timing differences vs book adjustments
│   ├── statement.py      # BRS (adjusted-balance method) + journal entries
│   └── report.py         # Excel, Markdown and console output
├── data/                 # sample bank statement and cash book
├── output/               # generated reconciliation pack
└── tests/                # pytest unit and end-to-end tests
```

## Accounting logic

**Sign convention.** Amounts are signed from the company's point of view: money into the bank is positive (bank deposit, cash book debit) and money out is negative (bank withdrawal, cash book credit). The two sources can then be compared directly.

**Which side does an item go on?**
- If the **books are right and the bank hasn't caught up yet**, it's a timing difference and adjusts the *bank* balance. No entry is needed; it should clear next month.
- If the **bank is right and the books are missing or wrong**, it adjusts the *book* balance and needs a journal entry.

**Suggested journal entries.** For example:

| Item | Entry |
|---|---|
| Bank charges | Dr Bank Charges / Cr Bank |
| Interest credited | Dr Bank / Cr Interest Income |
| Dishonoured cheque | Dr Accounts Receivable (customer) / Cr Bank |
| Unidentified receipt | Dr Bank / Cr Suspense (until the customer is identified) |
| Duplicate payment voucher | Dr Bank / Cr original expense ledger |

## Skills demonstrated

- Month-end close and bank reconciliation (BRS) under the adjusted-balance method
- Identifying and resolving reconciling items: timing differences, errors, and unrecorded transactions
- Internal-control thinking: integrity checks, duplicate detection, ageing of stale items, audit trail
- Process automation with Python (pandas) and Excel reporting (openpyxl)

## Possible extensions

- One-to-many matching (one bank deposit covering several customer receipts)
- Fuzzy matching on narration text for unidentified receipts
- Carry forward last month's outstanding items automatically
- Direct import from Tally / QuickBooks / Zoho Books exports

---

*All company names, accounts and transactions in this project are fictional.*
