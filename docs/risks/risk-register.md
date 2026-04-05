# Risk Register

## Current Risk Classification

- Tier: medium
- Owner: Adam Goodwin
- Last reviewed: 2026-04-05

## Key Risks

| ID | Risk | Likelihood | Impact | Controls | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-001 | External governance preflight cannot run when `GOVERNANCE_HOME` is not configured. | Medium | Medium | Explicit exception record `EX-2026-04-05-governance-home`; local doc review in same task. | Adam Goodwin | Open |
| R-002 | Probe agents may misidentify or miss tools in unusual local environments. | Medium | Medium | Short command timeouts, visible command log, bounded read-only probes, manual verification path in runbook. | codex session | Open |
| R-003 | Desktop launcher can become stale if the repository is moved after installation. | Medium | Low | Reinstall script, documented recovery steps, launcher path kept explicit. | Adam Goodwin | Open |
| R-004 | Filesystem mapping could scan a broader area than a user intended. | Medium | Medium | Opt-in root selection, no automatic full-system crawl, local-only processing, visible selected roots in UI. | codex session | Open |
| R-005 | Local AI coaching may produce incomplete or slightly incorrect explanations. | Medium | Medium | Local model status visibility, prompt grounded in the actual report/map, friendly but bounded coaching style, user can inspect raw findings directly. | codex session | Open |
