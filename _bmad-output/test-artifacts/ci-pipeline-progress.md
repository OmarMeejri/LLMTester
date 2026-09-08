---
stepsCompleted: ['step-01-preflight', 'step-02-generate-pipeline', 'step-03-configure-quality-gates', 'step-04-validate-and-summary']
lastStep: 'step-04-validate-and-summary'
lastSaved: '2026-09-08'
---

# CI/CD Pipeline Setup — LLMTester

## Step 1: Preflight

- **Git repository**: OK (`.git/` present, branch `develop`, up to date with `origin/develop`)
- **Remote**: `origin` → `git@gitlab.dom.tti:geniatesting/LLMTester.git`
- **Uncommitted change detected**: `Jenkinsfile` deleted in working tree (not committed). Flagged to user — not modified by this workflow.
- **Test stack type**: `backend` (Python) — no frontend indicators found; `pytest.ini` + `requirements.txt` + `tests/` present.
- **Test framework**: `pytest`, config in `pytest.ini` (markers: `regression`, `security`)
- **Local test run**: `pytest -m "regression or security" --junitxml=results.xml` → **4 passed**
- **CI platform**: `jenkins` (user choice — repo previously had a Jenkinsfile; user wants Jenkins pipeline, not GitLab CI, despite GitLab-hosted remote)
- **Environment context**:
  - No `.python-version` / `pyproject.toml` found — no pinned Python version in repo
  - Dependency manager: `pip` via `requirements.txt` (single package: `pytest`)
  - Caching strategy: pip cache keyed on `requirements.txt` hash

## Step 2: Generate CI Pipeline

- **Execution mode**: `sequential` (no subagent/agent-team runtime probing available in this session)
- **Output path**: `{project-root}/Jenkinsfile` (LLMTester repo root) — regenerated to replace the previously-deleted (uncommitted) Jenkinsfile, per user's platform choice
- **Contract testing**: skipped (`tea_use_pactjs_utils: false` in config)
- **Pipeline design** (adapted from `jenkins-pipeline-template.groovy`, rewritten for Python/pytest — the template is Node/Playwright-oriented and had no reusable content for this stack beyond stage names):
  - `Validate Parameters` — allow-lists `TEST_MARKERS` against `{regression, security}` (from `pytest.ini`) and validates `GIT_REF` against a safe branch-name pattern, before any value is used in a shell command or `pytest -m` expression (script-injection prevention)
  - `Checkout` — `git` step against the real SSH remote (`git@gitlab.dom.tti:geniatesting/LLMTester.git`); placeholder Jenkins credential id `gitlab-ssh-credentials` — **user must confirm/create this credential in Jenkins**
  - `Install` — creates `.venv`, installs `requirements.txt` plus `pytest-xdist`, `pytest-cov`, `ruff` (added for parallelism, coverage, and lint — none were in the original `requirements.txt`); stashes `.venv` for reuse by parallel shards
  - `Lint` — `ruff check .` (zero-config; no linter was previously configured in the repo)
  - `Test` — parallel shards by marker (`Shard - Regression`, `Shard - Security`), each with `pytest-xdist -n auto`, per-shard coverage + JUnit XML output
  - `Burn-In` — 10x re-run loop on `changeRequest()` or timer trigger, using the same allow-listed marker expression
  - `post.always` — archives `results-*.xml` / `coverage-*.xml` and publishes JUnit results
- **Open items flagged to user**:
  - Confirm Jenkins credential id for SSH checkout (`gitlab-ssh-credentials`)
  - Confirm agent has `python3` available, or adjust `PYTHON_BIN`
  - `pytest-xdist`, `pytest-cov`, `ruff` are not yet in `requirements.txt` — recommend adding them so local runs match CI

## Step 3: Quality Gates & Notifications

- **Burn-in**: skipped by default per stack-conditional rule (`test_stack_type: backend` — deterministic tests, no UI flakiness). Removed the Burn-In stage drafted in step 2; left a commented re-add snippet in the Jenkinsfile in case the regression suite grows and flakiness appears. User did not request an override.
- **Quality gates**:
  - `security` marker treated as P0 — 100% pass required (any failure fails the build; already true via pytest's non-zero exit)
  - `regression` marker treated as P1 (target ≥95%) — enforced identically to P0 for now given the suite's small size (4 tests total); documented as a policy to revisit with a pass-rate threshold script once the regression suite is large enough for partial tolerance to be meaningful
- **Notifications**: user chose **email**. Added `NOTIFY_EMAIL` build parameter (empty by default = disabled) and a `mail` step in `post.failure`, including build URL and artifact link. **Open item**: user must supply the actual distribution list to use as the parameter default (or set it at the job level in Jenkins).

## Step 4: Validate & Summary

### Validation against checklist.md

- Config file created at correct path: `Jenkinsfile` ✅
- Stages and sharding configured: 2 marker-based shards (regression, security) ✅
- Burn-in: intentionally skipped per backend-stack rule (documented) ✅
- Artifacts: `results-*.xml` / `coverage-*.xml` archived + JUnit published ✅
- Secrets/credentials documented: `docs/ci-secrets-checklist.md` ✅
- **Caught and fixed during local validation**: default `ruff` ruleset failed on pre-existing `tests/test_sample.py` (import-sort rule `I001`) — scoped the Lint stage to `--select=E9,F` (real errors only) so the first CI run isn't blocked by unrelated style debt. Verified locally (Windows venv) that both the scoped lint check and both marker shards (`pytest -m regression`, `pytest -m security`, each with `-n auto` + coverage + junitxml) pass.
- Helper scripts created and validated: `scripts/ci-local.sh`, `scripts/test-changed.sh` (executable, correct commands)
- Documentation created: `docs/ci.md`, `docs/ci-secrets-checklist.md`
- `.gitignore` updated to exclude `.venv/`, `results-*.xml`, `coverage*.xml`, `.coverage`, `htmlcov/`

### Completion Summary

- **CI platform**: Jenkins — `Jenkinsfile` at repo root
- **Key stages**: Validate Parameters → Checkout → Install → Lint → Test (2 parallel marker shards) → post (archive + JUnit + email-on-failure)
- **Artifacts**: `results-regression.xml`, `results-security.xml`, `coverage-regression.xml`, `coverage-security.xml`
- **Notifications**: email via `NOTIFY_EMAIL` param (currently empty/disabled — needs a real address)

### Open items for the user (not resolved by this workflow — require Jenkins/infra access or a decision)

1. Confirm/create the `gitlab-ssh-credentials` Jenkins credential (SSH key with access to the GitLab repo)
2. Set a real `NOTIFY_EMAIL` value (job default or per-run) for failure emails to be delivered
3. Confirm Jenkins agents have `python3` on PATH (or adjust `PYTHON_BIN`)
4. Decide whether to commit the previously-deleted-then-regenerated `Jenkinsfile` (currently modified but uncommitted in the working tree)
5. Consider adding `pytest-xdist`, `pytest-cov`, `ruff` to `requirements.txt` so local dev installs match what CI installs
6. Consider adopting full `ruff` style rules later (currently scoped to errors-only) — would require first cleaning up existing style debt in `tests/test_sample.py`

### Next steps

1. Review `Jenkinsfile`, `docs/ci.md`, `docs/ci-secrets-checklist.md`, `scripts/ci-local.sh`, `scripts/test-changed.sh`
2. Commit and push
3. Create the Jenkins job (or update the existing one) pointing at this `Jenkinsfile`
4. Set up the credential and mail server per `docs/ci-secrets-checklist.md`
5. Trigger a first build and verify all stages pass
