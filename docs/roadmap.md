# Roadmap

## Current Baseline

The application currently provides local stack review, selected-root filesystem mapping, share summaries, read-only maintenance diagnostics, separated Chat, Gemma-backed Request Desk reasoning, Approval Queue, local maintenance history, guarded low-risk action execution, deeper display/dock investigation planning, browser fallback mode, local Ollama-backed coaching, and platform setup/release guidance.

## Chunk 1: Governance And Release Hygiene

Status: completed.

- Initially keep governance level `1` and autonomy level `A1`.
- Initially keep execution disabled for generated maintenance and request plans.
- Snapshot the current supervised maintenance milestone in version control.
- Update the risk register for maintenance diagnostics, request planning, Windows/browser support, and approval-plan risks.
- Remove stale governance-path references from exception/risk docs.
- Clean duplicate wording in architecture and user-facing docs.

## Chunk 2: Platform-Specific Plan Hardening

Status: completed.

- Split maintenance plan generation by platform instead of reusing Linux commands for every operating system.
- Add Windows-native plan text for event logs, route/DNS inspection, package-manager review, and settings requests.
- Add Linux desktop-environment detection hints for GNOME, KDE, Xfce, COSMIC, and unknown sessions.
- Add tests that mock Linux and Windows diagnostics separately.
- Ensure unsupported platforms return explicit triage plans rather than weak command guesses.

## Chunk 3: Request Desk Expansion

Status: completed.

- Expand request families beyond cursor/pointer size:
  - display scaling, brightness, night light, and refresh rate
  - display/dock investigation for rotated external monitors, hidden screen regions, and pointer jitter
  - audio input/output selection and volume issues
  - network/DNS troubleshooting
  - package/update repair planning
  - Docker/container cleanup planning
  - startup app review
  - slow-computer guided triage
- Route unknown requests into a clarifying triage flow.
- Add request-plan tests for each supported family.
- Keep all generated plans approval-required and non-executing.

## Chunk 4: Maintenance History And Evidence

Status: completed.

- Add a local history/archive module for diagnostic snapshots, request plans, approval decisions, and future action results.
- Store records under a clear local-only directory such as `history/` or user-selected app data.
- Add a history view in GTK and browser mode.
- Add “known-good lessons” only when evidence supports them.
- Keep history exportable for support handoff.

## Chunk 5: Coach And UX Separation

Status: completed.

- Separate the combined coach page into clearer surfaces:
  - Chat
  - Request Desk
  - Approval Queue
  - History
- Make approval-required plans scannable with risk, reversibility, privilege, and exact commands.
- Add better empty states and “what changed since last run” summaries.
- Keep browser mode as the cross-platform baseline for Windows and Linux distributions.

## Chunk 6: Packaging And Sharing

Status: completed.

- Add setup guides for Ubuntu/Debian, Fedora, Arch, and Windows browser mode.
- Document Ollama setup and supported model tags.
- Add launcher/install guidance per platform.
- Decide whether to introduce packaging metadata such as `pyproject.toml`.
- Add release checklist coverage for Linux native mode and browser fallback mode.

## Chunk 7: Approved Action Runner Contract

Status: completed.

- Define the action-runner contract before implementation:
  - exact command preview
  - expected effect
  - privilege requirement
  - reversibility
  - timeout
  - output capture
  - post-check
  - rollback notes
- Require explicit per-action confirmation.
- Record approved actions and outputs in history.
- Keep privileged actions separated from normal diagnostics.

## Chunk 8: Guarded Maintenance Actions

Status: completed.

- Add a narrow action runner for reversible or low-risk maintenance tasks only after Chunk 7 is complete.
- Require per-action confirmation and visible logs.
- Start with user-space actions before any privileged actions.
- Reassess risk, autonomy, documentation, and approval controls before enabling privileged operations.
- Do not introduce autonomous execution until the tool has a long safety record.

## Chunk 9: Guarded Execution Enablement

Status: completed.

- Keep project controls at governance level `1` and autonomy level `A1`, with `action_runner_enabled: true` for user-approved guarded execution.
- Make the desktop Execute button run enabled low-risk plans instead of only showing blocked review text.
- Keep execution limited to exact, reversible, non-privileged commands in the guarded catalog.
- Keep privileged, destructive, placeholder, medium-risk, and unsupported plans blocked with visible reasons.
- Record completed, failed, and blocked action attempts in local history.

## Chunk 10: Interactive Request Desk

Status: completed.

- Add a Send button and Enter-to-send behavior for request intake.
- Keep a visible request conversation instead of jumping straight from a text field to a plan.
- Ask plain follow-up questions when the request is too vague.
- Prepare the guarded plan from the accumulated conversation once enough detail is present.

## Chunk 11: Gemma Reasoning Brain

Status: completed.

- Route Request Desk intake through local Gemma 4 when Ollama is available.
- Collect bounded read-only request evidence before Gemma asks the user for details.
- Ask Gemma for structured JSON containing request family, readiness, clarification questions, and reasoning summary.
- Accept only whitelisted request families from the model before preparing a deterministic guarded plan.
- Keep command selection, execution eligibility, approval controls, and guarded catalog enforcement outside the model.
- Analyze completed guarded action output with Gemma so Execute produces useful findings and next-fix direction.
- Simplify the desktop Request Desk and Approval Queue so the default view is a plain-language current recommendation and selected-fix card.
- Add Request Desk in-place execution so the user does not have to switch tabs to run the current guarded recommendation.
