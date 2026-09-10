# Expense dashboard data

Prepare category totals for a personal spending dashboard.

- Export summarizeExpenses(records). Each record has category (string) and cents (a non-negative safe integer). Additional fields are ignored.
- Trim category whitespace, keep case, and combine matching categories. Empty categories, non-string categories, invalid cents, non-object records, or non-array input throw TypeError.
- Return an array of { category, cents, count } sorted by cents descending. Break ties by category ascending using JavaScript string < comparison (not locale-specific sorting).
- Throw RangeError if any combined category total exceeds Number.MAX_SAFE_INTEGER. Empty input returns []. Do not mutate the input array or its records.

Start in `main.js`. Keep public signatures and types. The starter deliberately has no implementation.

Run `node --test --test-reporter=spec` in this folder. The gym restores the original grading files for each run. No external dependencies or network access are needed.

## Documentation

- [Map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)
- [Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [Safe integers](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isSafeInteger)
