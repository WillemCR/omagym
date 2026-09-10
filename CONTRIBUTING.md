# Contributing

Omagym keeps practice in real project folders and gives feedback without writing the learner's solution. Changes should preserve that boundary and the terminal-only workflow.

Complete the setup in [README.md](README.md). The full regression suite also requires the Rails bundle for its real Ruby reporter fixture: run `./bin/omagym modules add rails` in a development checkout with compatible system Ruby. Then run:

```sh
npm run check
npm test
npm run build
npm audit
```

`npm run lint` is available as a diagnostic, but the inherited lint baseline currently reports 53 errors across app effects, accessibility rules, copied UI components and curriculum fixtures. It is not a release or CI gate yet. Type checking, tests and the build are enforced; do not present them as a clean lint result.

The regression suite uses temporary directories, real local HTTP listeners and Node/Ruby reporter fixtures. It does not require an agent login or open desktop windows. Restricted containers must permit loopback sockets. Real exercise runs also require Bubblewrap user namespaces and the relevant system toolchains.

GitHub Actions runs type checking, the regression suite, the production build and npm's high-severity advisory check. Desktop integration and isolated browser/compiler exercises need separate validation on a compatible Linux desktop; a green CI run does not certify those paths.

## Changes

- Describe the behavior being fixed and how you checked it.
- Keep listeners on loopback and preserve learner files on updates.
- Keep tool arguments structured; never interpolate project names, paths or model output into shell code.
- Do not commit workspaces, generated exercises, local feedback, logs, credentials or model reference candidates.
- Update documentation when commands or setup requirements change.
- Use small changes; avoid unrelated formatting of the existing codebase.

## Curriculum

The catalog lives in `curriculum/*.json`; each project points to a starter directory. Copy a nearby project's structure for the same track. Include a concrete brief, editable entry file, canonical test files, expected check names and official documentation URLs.

Tests should exercise observable behavior. Run the unsolved starter: it must compile/load, report every expected check and fail meaningful assertions. Independently verify a temporary reference implementation passes every check. Remove that reference before preparing a contribution. Do not turn source-text comparisons, absent files or compilation errors into the learning objective.

The runner restores protected files in its execution copy. Learner changes must never alter the canonical tests or metadata used for scoring. Missing and skipped checks remain incomplete.

## Manual release checks

On Omarchy, start a new session, save a change externally, run tests, request feedback and resume after closing one session window. Confirm stale results are marked, old unrelated windows stay in place, and ending a session preserves files. For web changes, exercise a real Chromium suite and the separate-origin preview.

Use temporary projects for destructive fixtures. Keep any private local verification notes outside tracked files.

## Dependency maintenance

`package.json` overrides `sharp` to 0.35.4 because the current Cloudflare tooling pins an older release affected by GHSA-rgj7-g3m4-5g8c. Recheck the upstream dependency and npm audit before removing this override. Keep React, React DOM and React Server DOM on matching versions.

## Omarchy plugin

`manifest.json` and `plugin/OmagymWidget.qml` provide the native bar launcher. The first-click setup in `scripts/plugin-launch.py` maintains a separate app checkout under the user data directory; do not put dependencies or learner data in the removable plugin folder. Plugin sources must remain free of symlinks for Omarchy’s validator.

Validate a clean source export with `omarchy plugin validate <folder>`. The regular regression suite exercises setup ownership, update preservation, busy-backend refusal and concurrent installer locking. On Omarchy, additionally load the widget in Quickshell and run setup in an isolated absolute `XDG_DATA_HOME` with `--setup-only --no-packages --no-launcher` before testing on the desktop. Native plugin validation and Quickshell integration are local checks, not part of the Ubuntu CI job.

Language modules are defined in `gym/modules.py`. Keep system package management outside Omagym. Go-only setup must not inspect Ruby or install gems; Ruby-only setup must not pull Rails. Test failed setup, disabling modules, preservation of learner files, and backend enforcement as well as the chooser.
