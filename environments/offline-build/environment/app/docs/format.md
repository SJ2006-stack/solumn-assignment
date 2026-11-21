# Journal and trial balance

A journal is a sequence of transactions. A transaction header is a date
`YYYY-MM-DD`, a space, and a description. Posting lines are indented and
contain an account name. An amount, when present, is separated from the
account by at least two spaces. Exactly one posting in a transaction may
omit its amount; that posting balances the transaction. Amounts use a
dot as the decimal mark and two fractional digits. Debits are positive.
Credits are stored as negative minor units.

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
