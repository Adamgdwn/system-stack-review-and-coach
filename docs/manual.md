# Manual

## Purpose

System Coach and Maintenance Manager is a local-first desktop tool for understanding the machine it runs on. It explains installed development tools, maps user-selected filesystem roots, and offers local AI coaching through Ollama when available.

The next product direction is to grow this into a system maintenance and troubleshooting coach while keeping user approval at the center of any machine-changing action.

## Operating Model

- Local review probes run bounded, read-only checks.
- Filesystem mapping only scans roots selected by the user.
- AI coaching is grounded in the generated report and selected map.
- Gemma 4 through local Ollama is the Request Desk reasoning brain when available. Before it asks follow-up questions, the app collects bounded read-only evidence relevant to the request, such as display topology, audio devices, network routes, package-manager state, Docker usage, startup entries, performance basics, services, or recent logs.
- Maintenance diagnostics run as read-only observations and recommendations.
- Request Desk plans cover common troubleshooting families but remain approval-required previews.
- Display and dock requests collect monitor layout, rotation, dock, GPU, and session log evidence before any display setting or driver change is proposed.
- The Approval Queue collects prepared diagnostic and request plans in a single scannable place.
- Approved-action contracts gate execution. The Execute button runs only eligible low-risk plans after user approval.
- Local history records diagnostic snapshots and request-plan previews for later review.
- Any future repair or cleanup action must require explicit user approval before execution.

## Governance

This project is set to governance level `1` with agent autonomy `A1`.

In practical terms, the tool may inspect, summarize, reason about requests, and recommend. It may prepare changes or commands, but machine-changing actions require user approval before they are applied.

The current build can run eligible low-risk guarded plans when the user presses Execute. Gemma can classify the request family, but it cannot invent executable commands or bypass the guarded catalog. Plans that are privileged, destructive, unsupported, or not exact remain blocked and may be recorded in history.

After an eligible plan runs, Gemma reviews the captured output and summarizes what was found, the most likely cause, and the best next fix direction. This keeps Execute useful for investigation plans as well as direct low-risk setting changes.

## Common Workflows

1. Launch the desktop app with `bash launchers/run-system-coach.sh`.
2. Run a local review to inspect the current environment and installed tools.
3. Optionally scan selected roots to discover projects and configuration files.
4. Ask the local coach questions about the detected stack or selected roots.
5. Use Request Desk as a conversation. Type a request, press Enter or Send, answer any follow-up questions, and let the desk prepare a guarded plan from the accumulated context.
6. Read the Current Recommendation for the problem, evidence, recommended action, and execution status.
7. Press Execute Current Recommendation from Request Desk when the current guarded plan is the one you want to run.
8. Use the Approval Queue when choosing between multiple maintenance and request plans.
9. Review the History view when comparing recent diagnostics or preparing a support handoff.
10. Use Chat for questions about the current report, diagnostics, request plan, or selected roots.
11. Copy a share summary when a plain-language environment overview is needed.

## Maintenance Direction

The maintenance-manager expansion should prioritize:

- read-only system health diagnostics
- clear severity and evidence for each finding
- guided troubleshooting flows for common symptoms
- command previews before any fix is run
- auditable logs of checks, recommendations, and approved actions
- Windows and Linux browser-mode support, with native Linux GTK mode where GTK is installed
