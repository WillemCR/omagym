# Equal-height pricing cards

Use layout primitives to align calls to action without hard-coded card heights.

## Your brief

- Preserve the two .plan articles in .plans. At 1000px viewport show two equal-width, equal-height cards; at 390px stack them without page overflow.
- Place each Choose link at the bottom of its card; their bottom edges align on desktop despite different content lengths. Cards must grow if content grows.
- Each card has 24px padding; Club has a solid 3px border rgb(30, 64, 175). Choose links are block-level clickable areas at least 44px tall.
- Apply a transform transition to Choose links with a normal duration greater than zero; under prefers-reduced-motion reduce, transition duration becomes 0s.

## Work and check

Start in `index.html`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [MDN: CSS grid layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout)
- [MDN: media queries](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries/Using_media_queries)
- [MDN: prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
