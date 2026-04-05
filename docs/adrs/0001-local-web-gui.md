# ADR 0001: Use a Local Web GUI for the Stack Coach

## Status

Accepted

## Context

The project needs a GUI that is approachable for new to intermediate coders, runs locally, and can be launched from the desktop. A native Tkinter interface would have been a simple dependency-light option, but the target environment does not include the `tkinter` module for Python 3.12.3.

## Decision

Build the application as a local Python web server with a browser-based interface, and launch it through a desktop entry that starts the local server.

## Consequences

- The GUI remains dependency-light and works with the installed Python runtime.
- The desktop launcher experience is preserved by opening the browser automatically.
- The application can expose a small local API for future features without changing the presentation model.
- The browser becomes part of the runtime dependency chain.

