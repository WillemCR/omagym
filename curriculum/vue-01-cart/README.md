# Trail snack cart

Practice reactive quantities and computed totals in a two-item cart.

## Your brief

- Show numeric inputs labelled Apples quantity (unit price €1.50) and Nuts quantity (€2.25), both initially zero.
- Allow integer quantities from 0 to 10 inclusive. Show a status named Total formatted €N.NN and update it when either quantity changes.
- Provide Checkout, disabled when the total is zero or either quantity is invalid (blank, non-integer, negative or above ten). Show Invalid quantity while invalid.
- Clicking Checkout on a valid non-empty cart shows Order placed, resets both quantities to zero and resets the total.

## Work and check

Start in `src/App.vue`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [Vue: reactivity fundamentals](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)
- [Vue: form input bindings](https://vuejs.org/guide/essentials/forms.html)
