# Action states

Practice utility variants for pointer, keyboard and disabled states.

## Your brief

- Keep buttons #save (Save progress, enabled) and #locked (Locked, disabled). Style through Tailwind utilities.
- Both buttons have at least 44px height, 16px horizontal padding and 8px border radius. Save progress has a non-transparent background which changes on hover.
- Keyboard focus on Save progress has a visible solid outline at least 2px wide with at least 2px offset. Locked is excluded from tab order by native disabled semantics, has opacity 0.5 and cursor not-allowed.
- Save progress background changes use a nonzero transition normally. Under reduced motion, transition duration is zero. Moving the pointer away restores the original background.

## Work and check

Start in `index.html`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [Tailwind: responsive design](https://tailwindcss.com/docs/responsive-design)
- [Tailwind: hover, focus and other states](https://tailwindcss.com/docs/hover-focus-and-other-states)
