# Journal and trial balance

A journal is a sequence of transactions. A transaction header is a date
`YYYY-MM-DD`, a space, and a description. Posting lines are indented and
contain an account name. An amount, when present, is separated from the
account by at least two spaces. Exactly one posting in a transaction may
omit its amount; that posting balances the transaction. Amounts use a
dot as the decimal mark. A leading `-` is a negative amount. Debits are
positive. Credits are stored as negative minor units.

A line `currency CODE` sets the currency for the transactions that follow.
Known codes:

| Code | Minor digits |
| --- | --- |
| USD | 2 |
| JPY | 0 |
| BHD | 3 |

A journal with no currency line is USD. Extra fractional digits are rounded
per account when the amount is parsed. An account rounds HALF_UP when one
of its segments is `tax`. Every other account rounds HALF_EVEN. HALF_UP
breaks an exact tie away from zero. HALF_EVEN breaks an exact tie toward
the even minor unit. Digits past an exact 5 still round away from zero.

Account names are lowercase segments of letters, digits, and underscores,
separated by colons.

`;` starts a comment.

The trial balance lists accounts in sorted order:

```
TRIAL BALANCE
account                  debit       credit
<account left, width 24> <debit right, width 12> <credit right, width 12>
```

A positive minor-unit total is a debit. A negative total is a credit.
The other column is empty. There is one trailing newline after the last row.
