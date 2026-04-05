# Exception Record

## Metadata

- Exception ID: EX-2026-04-05-governance-home
- Project: system-stack-review-and-coach
- Standard: Governance preflight execution
- Status: Closed
- Approval date: 2026-04-05
- Review date: 2026-04-05

## Deviation

The repository required `bash scripts/governance-preflight.sh` before substantial changes. The script depended on an external governance repository referenced through `GOVERNANCE_HOME`, and that dependency was not configured in the local environment at the time the exception was opened.

## Justification

The project work needed to proceed in the local environment while the governance repository location was being verified and wired into shell startup.

## Risk Introduced

Before closure, an external policy check could have been skipped, increasing the chance that a repo-level governance requirement outside this repository would be missed.

## Compensating Controls

The governance repository was found at `/home/adamgoodwin/code/Rules of Development and Deployment`, `GOVERNANCE_HOME` was configured in shell startup, and the project preflight was rerun successfully.

## Approvals

- Project owner: Adam Goodwin
- Technical lead: codex session
