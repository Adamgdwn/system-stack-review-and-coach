# Exception Record

## Metadata

- Exception ID: EX-2026-04-05-governance-home
- Project: system-stack-review-and-coach
- Standard: Governance preflight execution
- Status: Open
- Approval date: 2026-04-05
- Review date: 2026-04-12

## Deviation

The repository requires `bash scripts/governance-preflight.sh` before substantial changes. The script depends on an external governance repository referenced through `GOVERNANCE_HOME`, and that dependency is not configured in the current environment.

## Justification

The project work needs to proceed in the present local environment, but the missing external governance repository prevents the automated preflight from running successfully.

## Risk Introduced

An external policy check may be skipped, which increases the chance that a repo-level governance requirement outside this repository is missed.

## Compensating Controls

The repository-level governance files were reviewed directly, the exception is documented explicitly, required docs are updated in the same task, and validation commands are run locally.

## Approvals

- Project owner: Adam Goodwin
- Technical lead: codex session
