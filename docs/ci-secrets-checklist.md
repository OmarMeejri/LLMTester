# CI Secrets & Credentials Checklist

Required setup in **Jenkins → Manage Jenkins → Manage Credentials** before the pipeline can run successfully.

- [ ] **`gitlab-ssh-credentials`** — SSH key credential with access to `git@gitlab.dom.tti:geniatesting/LLMTester.git`. Used by the `Checkout` stage. **Not yet confirmed to exist — create/verify before first run.**
- [ ] **Mail server configured** (Manage Jenkins → System → Extended E-mail Notification / built-in Mailer) — required for the `post.failure` `mail` step to actually send. No secret is stored in the pipeline itself; the SMTP config lives in Jenkins system settings.
- [ ] **`NOTIFY_EMAIL`** build parameter — not a secret, but must be set (job default or per-run) to an actual distribution list for failure notifications to go anywhere. **Currently defaults to empty (disabled) — user must supply the address.**

## Plugins required on the Jenkins controller/agents

- Pipeline
- JUnit
- Git

## Agent requirements

- `python3` available on PATH (adjust the `PYTHON_BIN` environment variable in the Jenkinsfile if the agent uses a different binary/alias)
- Standard POSIX shell (`sh` steps assume a Unix-like agent; the Jenkinsfile has not been adapted for Windows agents)

## Notes

- No credentials or secrets are hardcoded in the Jenkinsfile — the SSH credential is referenced only by its Jenkins credential ID (`gitlab-ssh-credentials`).
- `NOTIFY_EMAIL` is a plain build parameter, not a secret — it's just an email address.
