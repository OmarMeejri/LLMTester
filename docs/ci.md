# CI/CD Pipeline Guide

LLMTester runs its quality pipeline on **Jenkins**, defined in [`Jenkinsfile`](../Jenkinsfile).

## Stages

| Stage | What it does |
| --- | --- |
| Validate Parameters | Allow-lists `TEST_MARKERS` (`regression`, `security`) and validates `GIT_REF` before either is used in a shell command |
| Checkout | Clones the repo over HTTPS from GitHub (`github.com/OmarMeejri/LLMTester`) at the requested `GIT_REF` |
| Install | Creates `.venv`, installs `requirements.txt` plus `pytest-xdist`, `pytest-cov`, `ruff`; stashes the venv for reuse |
| Lint | `ruff check --select=E9,F .` — real errors only (syntax/undefined names); the repo has no prior lint config, so the full default ruleset is not enforced yet |
| Test | Two parallel shards, one per pytest marker (`regression`, `security`), each with `pytest-xdist`, coverage, and its own JUnit XML |
| (Burn-In) | Intentionally omitted — backend/deterministic stack. See the commented snippet in the Jenkinsfile if flaky tests start appearing |
| post.always | Archives `results-*.xml` / `coverage-*.xml`, publishes JUnit results |
| post.failure | Emails `NOTIFY_EMAIL` (if set) with the build URL and artifact link |

## Quality gate policy

- `security` tests are P0 — any failure fails the build.
- `regression` tests are P1 (target ≥95% pass rate) — currently enforced the same as P0. The suite now has 71 tests; revisit with a pass-rate threshold script if partial tolerance becomes worth the added complexity.

## Running the pipeline locally

```bash
./scripts/ci-local.sh          # mirrors the full CI pipeline: install, lint, test, coverage
./scripts/test-changed.sh      # runs only test files changed vs origin/main
```

## Build parameters

| Parameter | Default | Purpose |
| --- | --- | --- |
| `MR_ID` | _(empty)_ | Optional, for traceability |
| `GIT_REF` | `main` | Branch/ref to build |
| `TEST_MARKERS` | `regression,security` | Which pytest markers to run |
| `NOTIFY_EMAIL` | _(empty)_ | Distribution list emailed on failure; empty disables notifications |

See [`docs/ci-secrets-checklist.md`](ci-secrets-checklist.md) for required Jenkins credentials.

## Troubleshooting

- **Tests fail in CI but pass locally**: run `scripts/ci-local.sh` to reproduce the exact CI steps (venv, install, lint, test).
- **Lint failures**: only real errors (E9, F) are enforced today. If you want full style enforcement, add a `ruff.toml`/`pyproject.toml` config and update the Jenkinsfile's `ruff check` invocation accordingly — after first cleaning up existing style debt so the change doesn't break the pipeline on unrelated files.
- **Checkout fails with credential errors**: confirm the `github-creds` Jenkins credential exists (GitHub username + personal access token, or equivalent) and has access to `https://github.com/OmarMeejri/LLMTester.git`.
