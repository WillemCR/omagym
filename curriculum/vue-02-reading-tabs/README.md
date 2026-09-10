# Reading tabs

Build keyboard-operable tabs with useful reading content.

## Your brief

- Create a tablist named Reading guide, with tabs Overview, Examples and Resources in that order. Overview starts selected; exactly one tab is selected and keyboard tabbable.
- The visible tabpanel has the selected tab as its accessible name. Its text is Welcome to Vue, Practice makes progress, or Read the official guide respectively.
- Clicking a tab selects it. ArrowRight and ArrowLeft wrap through tabs, selecting and focusing the next tab. Home selects and focuses Overview; End selects and focuses Resources.
- Only the active panel is visible, and aria-selected plus tabindex stay synchronized with keyboard and pointer interaction.

## Work and check

Start in `src/App.vue`. The starter intentionally leaves the requirements unfinished. Run the browser suite in Omagym after saving; it opens your app in Chromium and checks the rendered DOM and behavior. Tests reset the page for each case. You may reorganize editable files while preserving the public behavior described above. No external services or downloads are needed. Ask the coach for observations and documentation when you get stuck.

## Documentation

- [Vue: reactivity fundamentals](https://vuejs.org/guide/essentials/reactivity-fundamentals.html)
- [Vue: form input bindings](https://vuejs.org/guide/essentials/forms.html)
- [WAI: tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)
