# Bank Reconciliation Statement - Sharma Traders Pvt Ltd

**Current Account XXXX4821** | As at **30 September 2026** | Amounts in INR

| Particulars | Amount |
|---|---:|
| **Balance as per bank statement** | **179,000.00** |
| &nbsp;&nbsp;&nbsp;&nbsp;Add: Deposit in transit | 36,500.00 |
| &nbsp;&nbsp;&nbsp;&nbsp;Less: Outstanding cheque (issued, not presented) | (37,400.00) |
| **Adjusted bank balance** | **178,100.00** |
| | |
| **Balance as per cash book** | **206,209.00** |
| &nbsp;&nbsp;&nbsp;&nbsp;Add: Duplicate posting in cash book | 2,360.00 |
| &nbsp;&nbsp;&nbsp;&nbsp;Add: Direct credit not recorded in books | 28,000.00 |
| &nbsp;&nbsp;&nbsp;&nbsp;Add: Interest credited by bank | 1,245.00 |
| &nbsp;&nbsp;&nbsp;&nbsp;Less: Direct debit (NACH/ECS) | (18,500.00) |
| &nbsp;&nbsp;&nbsp;&nbsp;Less: Posting error - amount mismatch | (270.00) |
| &nbsp;&nbsp;&nbsp;&nbsp;Less: Dishonoured cheque | (40,000.00) |
| &nbsp;&nbsp;&nbsp;&nbsp;Less: Bank charges | (944.00) |
| **Adjusted book balance** | **178,100.00** |
| **Unexplained difference** | **0.00** |

**Status: RECONCILED**

## Matching summary

- Bank statement lines: **20**
- Cash book entries: **18**
- Matched on reference + amount: **11**
- Matched on amount + date: **2**
- Amount mismatches: **1**
- Duplicate entries: **1**
- Timing differences: **3**
- Book adjustments required: **8**

## Timing differences (clear next month, no entry needed)

| Date | Voucher | Description | Category | Amount | Age (days) |
|---|---|---|---|---:|---:|
| 28-Sep-2026 | PV-0910 | Paid Patel Hardware | Outstanding cheque (issued, not presented) | (15,400.00) | 2 |
| 29-Sep-2026 | PV-0911 | Professional fees - Joshi Consultants | Outstanding cheque (issued, not presented) | (22,000.00) | 1 |
| 30-Sep-2026 | RV-0906 | Cheque deposited - Nair Distributors | Deposit in transit | 36,500.00 | 0 |

## Book adjustments (record in the cash book)

| Date | Ref | Description | Category | Effect on books |
|---|---|---|---|---:|
| 15-Sep-2026 | BANK-8 | NACH DR-TERM LOAN EMI | Direct debit (NACH/ECS) | (18,500.00) |
| 17-Sep-2026 | PV-0905 | Paid Verma Packaging - Bill VP/318 (books 7,250.00 vs bank 7,520.00) | Posting error - amount mismatch | (270.00) |
| 21-Sep-2026 | PV-0909 | Internet bill - September | Duplicate posting in cash book | 2,360.00 |
| 23-Sep-2026 | BANK-14 | NEFT CR-BHATIA ASSOCIATES | Direct credit not recorded in books | 28,000.00 |
| 26-Sep-2026 | BANK-17 | CHQ RETURNED-IYER TRADERS-INSUFFICIENT FUNDS | Dishonoured cheque | (40,000.00) |
| 26-Sep-2026 | BANK-18 | CHQ RETURN CHARGES INCL GST | Bank charges | (354.00) |
| 30-Sep-2026 | BANK-20 | INTEREST CREDITED | Interest credited by bank | 1,245.00 |
| 30-Sep-2026 | BANK-21 | ACCOUNT MAINTENANCE CHARGES INCL GST | Bank charges | (590.00) |

## Suggested adjusting journal entries

| Entry | Account | Debit | Credit |
|---|---|---:|---:|
| JE-01 | Loan / expense as per mandate - verify | 18,500.00 |  |
| JE-01 | To Bank - Current A/c XXXX4821 |  | 18,500.00 |
| JE-02 | Original ledger of PV-0905 - correct the amount | 270.00 |  |
| JE-02 | To Bank - Current A/c XXXX4821 |  | 270.00 |
| JE-03 | Bank - Current A/c XXXX4821 | 2,360.00 |  |
| JE-03 | To Original ledger of PV-0909 - reverse duplicate voucher |  | 2,360.00 |
| JE-04 | Bank - Current A/c XXXX4821 | 28,000.00 |  |
| JE-04 | To Suspense - identify customer / receipt |  | 28,000.00 |
| JE-05 | Accounts Receivable - reinstate customer balance | 40,000.00 |  |
| JE-05 | To Bank - Current A/c XXXX4821 |  | 40,000.00 |
| JE-06 | Bank Charges (expense) | 354.00 |  |
| JE-06 | To Bank - Current A/c XXXX4821 |  | 354.00 |
| JE-07 | Bank - Current A/c XXXX4821 | 1,245.00 |  |
| JE-07 | To Interest Income |  | 1,245.00 |
| JE-08 | Bank Charges (expense) | 590.00 |  |
| JE-08 | To Bank - Current A/c XXXX4821 |  | 590.00 |
