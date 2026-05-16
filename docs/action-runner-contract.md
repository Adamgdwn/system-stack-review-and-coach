# Approved Action Runner Contract

## Current State

The project remains at governance level `1` with autonomy level `A1`. Guarded action execution is enabled only when the user presses Execute and the selected plan passes the action-runner contract.

The Execute button is the user approval event. It runs only exact, low-risk, reversible, non-privileged commands in the guarded catalog. Some executable plans apply a current-user setting; others run read-only evidence commands so the next fix is grounded instead of guessed. Other plans remain visible for review and return blocked action results.

The reasoning layer may prepare plans that describe higher-risk, privileged, or broad system changes, but those plans do not automatically become executable. The action-runner contract remains the enforcement boundary between "the app can think through this" and "the app can run this now."

## Contract Fields

Each prepared maintenance or Request Desk plan may include `action_contract`:

- `contract_version`: contract schema name
- `id`: stable action id derived from the plan id
- `plan_id`: source plan id
- `plan_title`: source plan title
- `family`: request or maintenance family
- `status`: current runner status, such as `blocked`, `failed`, or `completed`
- `eligible_for_guarded_execution`: whether the plan shape is narrow enough for guarded execution
- `eligibility_notes`: reasons the plan is not eligible
- `approval_required`: always `true`
- `confirmation_phrase`: exact phrase preserved for audit and future stronger confirmation modes
- `execution_enabled`: `true` only when the plan passes governance, autonomy, catalog, and command checks
- `execution_gate`: reasons execution is blocked
- `command_preview`: exact command strings from the plan
- `expected_effect`: intended result
- `requires_privilege`: privilege flag
- `reversible`: reversibility flag
- `risk`: risk rating
- `timeout_seconds`: future execution timeout
- `output_capture`: future stdout/stderr capture policy
- `post_check`: checks to perform after a future action
- `rollback`: rollback notes
- `created_at`: contract creation timestamp

## Guarded Candidate Rules

A plan is eligible for guarded execution only when all of these are true:

- approval is required
- risk is `low`
- the plan is reversible
- the plan does not require privilege
- the plan family is in the low-risk guarded catalog
- exact commands are present
- commands do not contain placeholder text such as `<service-name>`
- every command executable is in the guarded catalog

The current low-risk catalog is:

- cursor size
- display brightness
- display dock evidence
- display layout fix
- display night light
- display refresh rate
- display scaling
- audio routing
- failed service evidence
- critical log evidence
- network and DNS evidence

## Execution Gate

Eligible plans can execute when all gate checks pass:

- governance level `1`
- autonomy level `A1`
- explicit `action_runner_enabled: true` in project controls
- the Execute button is pressed by the user
- every command runs through the subprocess runner with `shell=False`, strict timeout, and output capture

The implementation records completed, failed, and blocked action attempts through the same local history mechanism used for diagnostics and request plans.

## Future Runner Requirements

Before broadening execution:

- reassess project risk, governance level, and autonomy level again
- add post-check execution
- add rollback prompts
- add tests proving privileged and placeholder commands cannot run
- complete a fresh cold-eyes audit
