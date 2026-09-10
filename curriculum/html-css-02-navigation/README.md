# Accessible study navigation

Style a keyboard-friendly navigation bar that rearranges on small screens.

## Your brief

- Keep the Main navigation and its three links, with Lessons marked aria-current page. Keep Skip to content targeting the focusable main id content.
- At 390px, navigation links stack vertically. At 1000px, they sit in one horizontal row. Use 16px gaps and at least 12px padding on each navigation link.
- The current link has background rgb(30, 64, 175), white text and 8px radius. Keyboard-focused links have a visible solid outline at least 2px wide.
- The skip link is out of view until keyboard-focused, then visible inside the viewport. Activating it moves keyboard focus to main. No horizontal overflow on mobile.

## Work and check

Start in `index.html`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [MDN: CSS grid layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_grid_layout)
- [MDN: media queries](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_media_queries/Using_media_queries)
- [MDN: focus-visible](https://developer.mozilla.org/en-US/docs/Web/CSS/:focus-visible)
