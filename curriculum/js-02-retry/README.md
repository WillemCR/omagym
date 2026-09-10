# Resilient task runner

Retry a flaky operation with a testable delay policy, without real network requests.

- Export async retry(operation, options = {}). Options: attempts defaults to 3, delayMs defaults to 100, sleep defaults to an async function that waits the requested milliseconds.
- operation receives the 1-based attempt number. Return its first successful value, including undefined or other falsy values. Both synchronous throws and rejected promises count as failures.
- After a failed attempt, if another attempt remains, await sleep(delayMs * failedAttemptNumber). Never sleep before the first attempt, after success, or after the last failure.
- If all attempts fail, reject with the exact last thrown value (preserve object identity). If sleep rejects, propagate that exact reason immediately without another operation call.
- Before calling operation or sleep, reject with TypeError if operation or sleep is not a function, attempts is not an integer from 1 through 100, or delayMs is not a finite number from 0 through 60000. Tests inject sleep so no wall-clock delays are needed.

Start in `main.js`. Keep public signatures and types. The starter deliberately has no implementation.

Run `node --test --test-reporter=spec` in this folder. The gym restores the original grading files for each run. No external dependencies or network access are needed.

## Documentation

- [Async functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function)
- [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise)
- [Timers](https://nodejs.org/api/timers.html)
