# Architecture Overview

## Summary

System Stack Review and Coach is a local-only educational application that helps users understand the tools installed on their machine. It runs as a native GTK desktop application by default, executes local probe agents to inspect the environment, optionally maps user-approved filesystem roots, and renders the results in a desktop shell. It can also use a local Ollama-served model to answer interactive questions about the detected environment. A browser-hosted mode remains available as a fallback.

## Components

- `src/stack_review_coach/desktop_app.py`: Native GTK desktop shell and primary local user interface.
- `src/stack_review_coach/server.py`: Optional local HTTP server for browser fallback mode.
- `src/stack_review_coach/agents.py`: Defines local probe agents that execute version and capability checks for system tools.
- `src/stack_review_coach/ai_engine.py`: Connects to the local Ollama service and builds coaching prompts from the report and filesystem map.
- `src/stack_review_coach/knowledge.py`: Contains built-in explanations for common development tools and stack pairings.
- `src/stack_review_coach/scanner.py`: Performs opt-in filesystem mapping for user-selected roots and discovers projects and config files.
- `src/stack_review_coach/reporting.py`: Converts raw probe results into learner-friendly summaries, recommendations, and stack pattern matches.
- `src/stack_review_coach/web/`: Browser UI assets for the interactive learning experience.
- `launchers/`: Shell scripts for local execution and desktop installation.

## Data Flow

1. The user launches the application through the CLI script or desktop launcher.
2. The native GTK shell opens and requests local review data.
3. Probe agents execute local commands on the same machine and collect outputs such as versions, paths, and environment metadata.
4. If the user opts in, the filesystem mapper scans only the selected locations.
5. The reporting layer enriches those findings with explanatory knowledge and compatibility notes.
6. If the user asks a question, the desktop shell builds a local prompt from the report and optional map, then submits it to the local Ollama model.
7. The desktop shell renders the final report and AI coaching conversation for exploration and sharing.

In browser fallback mode, the local HTTP server exposes the same information through local endpoints.

No remote services are required, and no probe or filesystem results are transmitted off-machine by the application.

## Dependencies

- Python 3.12+
- Standard library modules only for runtime behavior
- GTK 3 via `python3-gi`
- A local Ollama service when interactive AI coaching is enabled
- Local operating-system commands when present, such as `python3`, `git`, `node`, or `docker`
- Read access for any folders the user chooses to map

## Key Decisions

- ADR 0001 selects a local web GUI because `tkinter` was not available in the target Python environment.
- Agent controls were reassessed to `A1` because the tool now uses bounded local probe agents to execute read-only inspection commands.
- Filesystem mapping is opt-in and scope-based to avoid surprising broad scans across the machine.
- Local AI coaching uses an on-device model through Ollama so stack questions can stay within the local environment.
