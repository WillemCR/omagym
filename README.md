# Omagym

Guided coding practice with your own editor, isolated tests, and a feedback-only coach.

Omagym opens a dedicated Omarchy workspace with your default editor, terminal, and a small browser companion for the project brief, tests, and feedback. You write the code. The coach reads your saved files and responds with observations, questions, and documentation links.

Prefer the terminal? Every practice operation also works from the CLI. A full browser dashboard includes a file manager and editor.

**Omagym is an independent community project. It is not affiliated with, officially supported by, or endorsed by DHH (David Heinemeier Hansson) or Omacom.** Please report Omagym issues in [this repository](https://github.com/WillemCR/omagym/issues).

## Install as an Omarchy plugin

On an x86-64 Omarchy laptop with the Quickshell plugin system:

```sh
omarchy plugin add https://github.com/WillemCR/omagym.git --enable
```

Click **<> Omagym** in your bar. First launch installs the shared app dependencies, builds the dashboard and asks which language modules you want. Choose Go without needing Ruby, Rails, Rust or Chromium. Existing plugin installations also get this choice the first time they update to modular setup; saved work is preserved.

**Omagym does not install or upgrade system packages.** If a selected module needs tools you do not have, it names the missing tools so you can install a compatible version yourself. Base setup needs Python, Git, Node 24+, npm and Bubblewrap with working user namespaces. Node is shared by the dashboard even when you only practice Go. First setup needs internet access for locked app dependencies; Ruby/Rails gems are downloaded only when you enable those modules. Your existing Codex login remains user-managed.

For terminal-driven setup instead of clicking the widget:

```sh
python3 ~/.config/omarchy/plugins/willemcr.omagym/scripts/plugin-launch.py --setup-only --modules go
omagym start 01-wordstats
```

The plugin source stays under `~/.config/omarchy/plugins/willemcr.omagym`. The runnable app, dependencies, workspaces and generated exercises stay separately in `${XDG_DATA_HOME:-~/.local/share}/omagym/app`. The app launcher is installed under `~/.local`; an existing Omagym launcher from another checkout is preserved instead of overwritten.

```sh
omarchy plugin update willemcr.omagym  # Click the widget afterward to apply app updates
omarchy plugin disable willemcr.omagym
omarchy plugin enable willemcr.omagym
omarchy plugin remove willemcr.omagym
```

Updating fast-forwards the managed app to the plugin's reviewed commit and rebuilds dependencies when needed. It refuses to overwrite app source edits or interrupt a busy owned backend. Saved learner work is preserved. Removing the plugin removes its bar integration; it keeps the app, its launchers and your practice data. To remove those launchers, run `python3 ~/.local/share/omagym/app/scripts/install-desktop.py --uninstall` (adjust for a custom `XDG_DATA_HOME`). Back up `workspaces/` and `generated/` before any manual app-directory removal.

This is a direct Git installation; no marketplace listing or upstream approval is required. If `omarchy plugin` is unavailable on your Omarchy version, use the manual setup below.

## Optional language modules

```sh
omagym modules                 # See enabled modules
omagym modules choose          # Change your selection interactively
omagym modules add go
omagym modules add ruby         # Small local Ruby bundle, no Rails
omagym modules add rails        # Rails also enables Ruby
omagym modules add web
omagym modules remove rails    # Keeps Ruby, dependencies and all your files
```

| Module | Additional requirements |
| --- | --- |
| `go` | System Go and a C compiler |
| `rust` | System Rust/Cargo and a C compiler |
| `javascript` | No extra runtime beyond shared Node |
| `web` | System Chromium; covers HTML, CSS, React, Vue and Tailwind |
| `ruby` | System Ruby 3.4+, build tools, and five locked local gems |
| `rails` | System Ruby 3.4+, build tools, and the full local Rails bundle |

The frontend and web tooling share the app's npm dependencies. Module selection controls optional system toolchain requirements and Ruby/Rails bundles; it does not split every JavaScript package into a separate download.

Selections live in `.runtime/modules.json`. A disabled track remains browsable, but tests, previews and project generation explain which module to enable. You can enable more later without reinstalling the app. Re-run `modules add ruby` or `modules add rails` if you deliberately change system Ruby or need to refresh that module’s locked bundle. An idle running backend restarts after module changes; active operations must finish first. Disabling modules never uninstalls packages, deletes gems, or deletes learner files. Existing manual checkouts retain access until you explicitly choose modules.

Non-interactive plugin setup can use `--modules go,javascript` or `--modules none`; without an explicit selection it prepares just the base app. For an existing plugin installation, `--choose-modules` opens the chooser again.

## Requirements

- Linux with Bubblewrap (`bwrap`) and permission to create user namespaces.
- Python 3.11+ and Node.js/npm. Use the version in `.node-version` (25.2.1) for reproducible builds.
- For Go: Go 1.23+ and a C compiler (the suite uses the race detector).
- For Rust: Rust and Cargo.
- For Ruby/Rails: Ruby 3.4 and the local gems installed below.
- For web tracks: Chromium at `/usr/bin/chromium`.
- For the coach and project designer: an installed, signed-in Codex CLI. Tests and editing work without it.
- For desktop sessions: Omarchy's launch helpers, Hyprland, and configured default applications. Terminal-only sessions need no compositor.

The runner currently expects Go, Rust, Ruby, Chromium and their libraries under `/usr`. Home-directory runtime managers for these tools are not yet supported inside the sandbox. Node installations outside `/usr` are explicitly mounted read-only.

Validated on x86-64 Linux with Python 3.14, Node 25.2.1, Ruby 3.4, Go 1.27 and Rust 1.98. Other distributions, architectures and default GUI applications may need adjustments.

## Install and start

Clone or download this repository into a permanent directory, then run these commands from its root:

```sh
python3 -m venv .venv
SHARP_IGNORE_GLOBAL_LIBVIPS=1 npm ci
npm run build

# Enable only what you want. Existing compatible system tools are required:
./bin/omagym modules add go

# Try it without installing a launcher:
./bin/omagym start 01-wordstats --terminal-only
```

Open [the local dashboard](http://127.0.0.1:4310/), or run `./bin/omagym brief`, `./bin/omagym test`, and `./bin/omagym coach` from the repository while this is your only active session.

To add the command and an application-launcher entry:

```sh
python3 scripts/install-desktop.py
omagym
```

Ensure `~/.local/bin` is on your `PATH`. The installer links to this checkout, so keep it in place. It does not install system dependencies or change your desktop configuration. Uninstall the launcher with `python3 scripts/install-desktop.py --uninstall`; your practice files remain.

## Practice

```sh
omagym list
omagym list --track ruby
omagym start 01-wordstats          # Default editor + terminal + companion
omagym start 01-wordstats --files  # Also open your default file manager
omagym start 02-ledger --no-editor
omagym start 01-wordstats --terminal-only
omagym start 01-wordstats --shell  # Enter a project subshell, no GUI
```

Save in your editor before running tests or asking the coach. Inside a project folder:

```sh
omagym brief
omagym test
omagym coach "What do my tests show?"
omagym status
omagym preview --open             # Web projects only
```

Elsewhere, supply `--project ID`. Commands accept `--json`. Test exit codes are 0 for passed, 1 for incomplete, 2 for operational errors and 3 for conflicts/busy.

`omagym resume` focuses a session and reopens missing windows. `omagym files` opens your default file manager. `omagym end` ends session tracking and returns to the previous workspace where possible; it keeps your windows, files and backend. Use an explicit project ID when several sessions are active.

Desktop integration was exercised with Neovim, Foot, Chromium and Nautilus. Unfamiliar apps may require manual window placement. Omagym does not move existing windows unless it can verify they belong to the session. Use `omagym resume ID --reopen` to explicitly retry a launch.

## Projects

| Track | Projects |
| --- | ---: |
| Go | 20 |
| Rust | 3 |
| Modern JavaScript | 3 |
| React | 3 |
| Vue | 3 |
| HTML | 3 |
| HTML + CSS | 3 |
| Tailwind | 3 |
| Ruby | 3 |
| Ruby on Rails | 3 |

All 47 built-in projects include a brief, unsolved starter, official documentation and behavioral tests. Go progresses from strings and maps to contexts, binary framing, middleware and transactions. Rails exercises use actual Rails components and in-memory SQLite. Web tests drive Chromium.

The browser library also lets you **Create a project** from a prompt. Codex designs a starter, tests and a private reference candidate. Omagym checks that the reference passes, the starter fails meaningful assertions, and browser starters load correctly. Only the unsolved project is published into your local library; temporary reference files are removed. Generation can take several minutes and continues when the dialog is closed. The chosen scope is guidance, not a completion-time guarantee.

## Feedback and privacy

The coach receives a bounded snapshot of eligible saved project files and the latest test results through your installed Codex CLI. It uses the existing login; Omagym does not store a separate API key. Coaching and generation send their prompts and supplied source content to your configured Codex service.

Feedback is limited to observations, reflection questions and approved official documentation links. Code, pseudocode and implementation instructions are prohibited. The agent has no editing action. Structured validation rejects obvious code and unapproved links, but semantic compliance still depends on model instructions.

The companion marks tests and feedback as outdated when saved files change. It cannot read unsaved editor buffers. One test, preview, coach or generation operation runs at a time.

## Local data and isolation

- `curriculum/`: shipped metadata, briefs, starters and canonical tests.
- `workspaces/<id>/`: your persistent source files, seeded only when missing.
- `generated/`: validated custom exercise templates and metadata.
- `.runtime/`: results, feedback, session records, logs and disposable caches.

The last three directories are ignored by Git. Ruby-only gems live in `.runtime/gems-ruby`; the full Rails bundle uses `.runtime/gems`. Back up both `workspaces/` and `generated/` to retain custom projects and your work. Omagym does not provide an off-machine backup.

Snapshots include up to 100 UTF-8 files, 128 KB per file and 600 KB total. Hidden paths, symlinks, dependency folders and common temporary files are excluded. Keep credentials out of exercise source.

Tests run in Bubblewrap with a private network namespace, no host home directory, read-only tool dependencies and writable temporary exercise/cache directories. Missing isolation fails closed. Canonical tests are restored in the execution copy, and missing or skipped checks cannot count as completion. This is a personal learning tool, not a hardened multi-user grader; see [security and limitations](SECURITY.md).

## Server and development

```sh
omagym server start
omagym server status
omagym server stop
```

Session commands start the backend automatically. The production dashboard uses loopback port 4310; previews use 4312. Logs are in `.runtime/server.log`. The launcher checks process identity, reuses its own running backend and refuses to interrupt an active operation or take over occupied ports.

For foreground production, run `npm start` after building. For development, stop production first, then run these in separate terminals:

```sh
.venv/bin/python -m gym.server --port 4311
npm run dev
```

Vite serves the dashboard on 4310 and proxies the Python API on 4311. Preview remains on 4312. The React/TypeScript frontend uses Vinext/Vite; the backend and CLI use Python's standard library. Filesystem access, compilers and the installed agent require the local backend.

See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and curriculum conventions. Dependency licenses and copied component attribution are listed in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

[MIT](LICENSE). Bundled component notices remain applicable.
