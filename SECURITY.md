# Security

Omagym is a local, single-user learning tool. Keep its HTTP listeners on loopback. Do not expose it directly to a LAN or the internet: the backend has no multi-user authentication or authorization model.

## Execution boundaries

Exercise code runs through Bubblewrap with a private network namespace and no host home directory. System tools, `/etc`, runtime helpers and installed dependencies are mounted read-only; temporary exercise files and runner caches are writable. Isolation is required and failures do not fall back to unrestricted execution.

These boundaries are not a hardened sandbox for hostile submissions. There are wall-time and output limits, but no CPU/memory/disk quotas. Caches are shared across local runs. Browser processes use `--no-sandbox` inside the outer Bubblewrap isolation. Do not use Omagym as a public grading service.

The server restores canonical tests in its execution copy and checks required results. This prevents accidental completion through missing/skipped tests; it is not tamper-proof scoring against deliberately hostile code.

## Agent access

Coaching sends eligible saved files and test results to the installed Codex CLI. Project generation sends your prompt and validation feedback. These features use your existing agent account and its service/data settings. Do not include secrets or confidential code unless you intend to share them with that service.

The coach uses read-only settings, disabled editing/shell actions and a structured response contract. Generated reference candidates are temporary and excluded from published exercise folders. Model instructions and response validation reduce solution leakage; they cannot guarantee perfect semantic compliance.

## Reporting

Once hosted on GitHub, use **Security → Report a vulnerability** if private reporting is enabled. If it is unavailable, open an issue asking the maintainer for a private reporting channel without including exploit details, credentials or private source. A dedicated security mailbox is not configured.

Only the latest development version is maintained at present. Security fixes will be documented in the repository; no response-time guarantee is offered.
