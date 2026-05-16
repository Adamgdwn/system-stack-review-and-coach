# Approved Action Runner Contract

## Current State

The project remains at governance level `1` with autonomy level `A1`. Action execution is disabled.

Chunks 7 and 8 establish the contract, guarded catalog checks, UI visibility, history records, and blocked execution result shape. They do not enable subprocess execution.

## Contract Fields

Each prepared maintenance or Request Desk plan may include `action_contract`:

- `contract_version`: contract schema name
- `id`: stable action id derived from the plan id
- `plan_id`: source plan id
- `plan_title`: source plan title
- `family`: request or maintenance family
- `status`: current runner status, usually `blocked`
- `eligible_for_guarded_execution`: whether the plan shape is narrow enough for future guarded execution
- `eligibility_notes`: reasons the plan is not eligible
- `approval_required`: always `true`
- `confirmation_phrase`: exact phrase a future runner would require
- `execution_enabled`: currently `false`
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

A plan is eligible for future guarded execution only when all of these are true:

- approval is required
- risk is `low`
- the plan is reversible
- the plan does not require privilege
- the plan family is in the low-risk guarded catalog
- exact commands are present
- commands do not contain placeholder text such as `<service-name>`

The current low-risk catalog is:

- cursor size
- display brightness
- display night light
- display refresh rate
- display scaling
- audio routing

## Execution Gate

Even eligible plans remain blocked until governance is reassessed. The current gate requires:

- governance level above `1`
- autonomy above `A1`
- explicit `action_runner_enabled: true` in project controls
- a matching confirmation phrase
- an implemented subprocess runner

The current implementation records blocked action attempts through the same local history mechanism used for diagnostics and request plans.

## Future Runner Requirements

Before enabling execution:

- reassess project risk, governance level, and autonomy level
- add per-action confirmation in the UI
- add subprocess execution with strict timeouts and output capture
- add post-check execution
- add rollback prompts
- add tests proving privileged and placeholder commands cannot run
- complete a fresh cold-eyes audit
