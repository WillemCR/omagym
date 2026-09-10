# Workshop registration

Use native HTML controls to make an accessible registration form without JavaScript.

## Your brief

- Create one form named Workshop registration, with required Name (text), Email (email), and Tickets (number, integer from 1 to 4, initially 1). Give controls names name, email, tickets.
- Add a required checkbox labelled Accept terms with name terms, and a Register submit button. The browser must reject empty fields, malformed email, unchecked terms and out-of-range or fractional tickets.
- Add a Track select with name track and options Go and Rust (values go and rust, default go). All labels must activate their controls.
- Use native HTML validation. A valid filled form must pass checkValidity and yield its entered values via FormData; no submission backend is required.

## Work and check

Start in `index.html`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [MDN: HTML elements](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements)
- [MDN: constraint validation](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Constraint_validation)
