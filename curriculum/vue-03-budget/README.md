# Weekend budget

Track a weekend budget with validation, removal and live category totals.

## Your brief

- Provide Description input, Amount numeric input, Category select (Food, Travel, Fun; default Food) and Add expense button. Reject blank descriptions and non-finite or non-positive amounts.
- On valid submission trim the description, add an expense to a list named Expenses and clear Description and Amount. Show each amount with two decimal places.
- Each row has Remove <description> button. Duplicate descriptions are independent expenses. A status named Total shows the sum as €N.NN.
- Provide a Filter category select (All, Food, Travel, Fun; default All). The list is filtered, but Total always includes all expenses. A status named Visible total shows the filtered sum as €N.NN. Empty visible lists show No expenses.

## Work and check

Start in `src/App.vue`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [Vue: reactivity fundamentals](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)
- [Vue: form input bindings](https://vuejs.org/guide/essentials/forms.html)
