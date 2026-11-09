# Omagym beta

The first beta targets a small group using x86-64 Omarchy with the Quickshell plugin system. Its core task is simple: install, open a project in your own editor, save changes, run meaningful tests, and return later without losing work. This is a release checklist and tester guide, not a declaration that every gate has passed.

Start with Go. Other installed language modules can be tested afterward. Coaching and project generation are optional and require your own signed-in Codex CLI; the core practice loop must work without them. Windows, macOS, other architectures, and hosted multi-user access are outside this beta's scope.

## First session

1. Check the [requirements](README.md#requirements). Base setup needs Python 3.11+, Node 24+, npm, Git, and working Bubblewrap isolation. Go also needs system Go and a C compiler. Setup reports missing tools; it does not install system packages.
2. Follow the [plugin installation instructions](README.md#install-as-an-omarchy-plugin). Click the dumbbell icon and choose Go. First setup downloads dependencies and builds the dashboard. If you already use Omagym, back up `workspaces/` and `generated/` in your app directory before testing updates.
3. Start `01-wordstats` from the picker or run `omagym start 01-wordstats`. Confirm the brief, editor, and terminal open. If desktop launch fails, try `omagym start 01-wordstats --terminal-only` and include the desktop failure in your report.
4. Run `omagym test --project 01-wordstats`. The unsolved starter should report failing checks. A compiler crash, missing tool, or no reported checks is a setup problem, not the intended starting point.
5. Edit and save `main.go` in the project folder shown by the session. Confirm old results become outdated, then run the tests again. Work through the brief until the checks pass, or tell us where the brief or feedback stops helping.
6. Close one session window, run `omagym resume 01-wordstats`, and confirm your saved work remains. Run `omagym end --project 01-wordstats`, then start the same project again. Ending tracking must preserve your files.
7. Optionally ask the coach for feedback. This sends eligible saved source files and test results through your installed Codex account. Feedback should help you reason without supplying a solution. Report unwanted solution disclosure privately if it includes your source.

If a command fails, keep its error and report the step. Do not delete your app or practice folders to retry. First-click setup can be retried after correcting missing tools.

## Send feedback

Use the [beta bug report](https://github.com/WillemCR/omagym/issues/new?template=beta-bug.yml) for failures. Include what you expected, what happened, and the smallest steps that reproduce it. For general feedback, [open an issue](https://github.com/WillemCR/omagym/issues/new) describing whether you could finish a project and what made you hesitate or stop.

Include your Omarchy version, editor, terminal, enabled modules, and the installed app commit. With the default plugin installation, get the commit with:

```sh
git -C "${XDG_DATA_HOME:-$HOME/.local/share}/omagym/app" rev-parse HEAD
node --version
python3 --version
omagym modules --json
omagym server status --json
```

For a manual checkout, run `git rev-parse HEAD` there. If setup failed before creating the app, report the plugin commit instead. The plugin source and installed app can differ until you click the widget after an update.

Share only the relevant error excerpt. Review output before posting; omit credentials, private source, and personal paths. Do not attach entire `.runtime/`, `workspaces/`, or `generated/` directories. Security issues follow [SECURITY.md](SECURITY.md#reporting).

## Maintainer release gates

Record the candidate commit and results when preparing each beta. Do not mark a manual gate complete based only on unit tests.

Preparation checks on 2026-10-30 passed locally with Node 24.13.0: clean `npm ci`, type checking, lint, all 111 regression tests, production build, and npm audit (no known vulnerabilities). A temporary source copy passed Omarchy plugin validation, fresh Go-only setup, and repeat setup. Isolated starter checks passed for one project each in Go, JavaScript, React, Vue, HTML, HTML + CSS, and Tailwind: starters loaded and reported meaningful failures with all expected checks observed. A temporary Go solution passed; saved changes invalidated old results and survived reopening. These checks do not certify all 52 exercises or replace the candidate's desktop and tester gates below.

A headless Chromium check against the production dashboard also passed: the editor saved a change, reload retained it, real Go test failures appeared, and the companion displayed the same saved results without browser page errors. That check did not cover desktop window behavior, reconnection after backend failure, or live AI calls.

Additional working-tree verification on 2026-11-09 used the real HTTP backend with a temporary practice directory and headless Chromium. Stopping and restarting that backend preserved an unsaved dashboard draft, which then saved successfully. A real Go starter run reported all eight expected checks with meaningful failures. After another backend restart, the companion reconnected automatically and retained the saved result and source.

A later isolated sweep exercised all 52 shipped starters: 240 observed leaf checks, 232 expected failures, eight passing defaults, and no missing checks or unavailable toolchains. All 15 web starters also compiled and rendered without browser errors. This checks starter execution and reporting, not every exercise contract against a correct solution. Real browser checks covered external-save conflicts, creating and recreating files, read-only test files, a passing Go implementation, shared outdated-result indicators, and React preview freshness. One live coach request correctly identified stale passing tests without supplying a solution; a controlled agent failure preserved earlier feedback, and stopping a busy backend was refused. One live Go generation survived a dashboard reload, validated its private reference, published an unfinished starter with all seven checks observed, and removed its private working files. These working-tree checks do not replace the candidate's native desktop, clean-installation, update, or independent-tester gates below.

A subsequent unlocked desktop check opened the real editor, terminal and companion in the dedicated Omagym workspace. Closing the terminal and resuming reopened only that terminal, preserving the editor and companion identities. Ending the session restored the preceding workspace while preserving source bytes and all three windows. Test windows were then closed explicitly. This used a temporary installation with existing dependencies, so clean installation and candidate update checks remain separate.

Background recovery checks passed all 119 Python tests. Injected generation failures verified that startup releases the busy lock, publication rollback preserves a workspace created during the operation, and a failed final status write does not hide a published project. Restart recovery preserves learner edits and matches the full generation ID recorded in new manifests. Older projects remain usable; interrupted legacy jobs without that ID cannot be reliably reconciled with a published project.

- [ ] Clean installation from the candidate commit succeeds in a fresh app directory, with only the selected modules required.
- [ ] Type checking, lint, all regression tests, production build, and the CI dependency audit pass against the candidate lockfile.
- [ ] A fresh Go starter fails meaningful assertions, a temporary correct implementation passes, and saved edits mark prior results outdated.
- [ ] The production dashboard and companion work in a browser: project selection, file saving, test results, errors, and reload/reconnect.
- [ ] On an actual Omarchy desktop, first-click setup, editor/terminal placement, resume, and end preserve work and leave unrelated windows alone.
- [ ] Update an older installation with saved work and a generated exercise; verify both survive. Verify a busy backend and local source edits block updates without data loss.
- [ ] With a tester account, coach and generation succeed; missing login and service failures produce actionable errors. Generation publishes an unsolved exercise with working tests and no reference solution.
- [ ] Exercise every optional module advertised as tested for this candidate. Record any untested modules in the release notes.
- [ ] A second person completes installation and a practice session without maintainer intervention.

When these gates pass, tag the tested commit as a beta and publish release notes with the installation steps, supported environment, known issues, and feedback link. The plugin currently installs and updates from the repository's default branch; a release tag alone does not pin plugin installs. Keep that branch on the tested candidate during invitations, and recheck changes before asking testers to update.

Defer new tracks, accounts, cloud hosting, and a larger feature set until this practice loop is reliable for testers.
