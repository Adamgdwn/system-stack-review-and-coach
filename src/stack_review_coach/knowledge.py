"""Reference knowledge for installed tools and compatibility notes."""

from __future__ import annotations

COMPONENT_KNOWLEDGE = {
    "python3": {
        "label": "Python",
        "category": "language",
        "role": "A general-purpose language that is great for automation, backend services, data work, and scripting.",
        "pairs_well_with": ["pip", "venv", "git", "docker", "uvicorn", "fastapi"],
        "learning_tip": "Use a virtual environment for each project so dependencies stay isolated.",
    },
    "node": {
        "label": "Node.js",
        "category": "language",
        "role": "A JavaScript runtime used for frontend tooling, servers, CLIs, and full-stack apps.",
        "pairs_well_with": ["npm", "pnpm", "typescript", "vite", "docker"],
        "learning_tip": "Most frontend tools depend on Node, even when the final app is not a Node backend.",
    },
    "npm": {
        "label": "npm",
        "category": "package-manager",
        "role": "The default package manager for JavaScript and Node.js projects.",
        "pairs_well_with": ["node", "typescript", "vite", "react"],
        "learning_tip": "Look in package.json to understand a project's scripts and dependency setup.",
    },
    "pnpm": {
        "label": "pnpm",
        "category": "package-manager",
        "role": "A fast, disk-efficient JavaScript package manager.",
        "pairs_well_with": ["node", "typescript", "vite", "monorepos"],
        "learning_tip": "pnpm uses a global content-addressable store, so installs are often faster and leaner.",
    },
    "git": {
        "label": "Git",
        "category": "source-control",
        "role": "The standard tool for tracking code changes, branching, and collaboration.",
        "pairs_well_with": ["github-cli", "vscode", "python3", "node"],
        "learning_tip": "If you're learning, focus first on status, add, commit, branch, pull, and push.",
    },
    "gh": {
        "label": "GitHub CLI",
        "category": "source-control",
        "role": "A command line companion for GitHub workflows like PRs, issues, auth, and automation.",
        "pairs_well_with": ["git"],
        "learning_tip": "Great for staying in the terminal while still working with pull requests and issues.",
    },
    "docker": {
        "label": "Docker",
        "category": "containers",
        "role": "Packages apps and their dependencies into portable containers.",
        "pairs_well_with": ["docker-compose", "python3", "node", "postgres", "redis"],
        "learning_tip": "Containers help you keep local environments closer to staging or production.",
    },
    "docker compose": {
        "label": "Docker Compose",
        "category": "containers",
        "role": "Starts and coordinates multiple related containers for local development or demos.",
        "pairs_well_with": ["docker", "postgres", "redis", "nginx"],
        "learning_tip": "Compose files are a helpful way to see an app's supporting services at a glance.",
    },
    "code": {
        "label": "VS Code",
        "category": "editor",
        "role": "A popular editor with strong support for extensions, terminals, debugging, and Git.",
        "pairs_well_with": ["python3", "node", "git", "docker"],
        "learning_tip": "Extensions often reveal what languages and workflows your environment is optimized for.",
    },
    "cursor": {
        "label": "Cursor",
        "category": "editor",
        "role": "An AI-enhanced editor built for coding workflows and repo navigation.",
        "pairs_well_with": ["git", "python3", "node"],
        "learning_tip": "If multiple editors are installed, teams often choose one as the default and keep others as optional.",
    },
    "java": {
        "label": "Java",
        "category": "language",
        "role": "A widely used language for enterprise apps, Android, and many backend systems.",
        "pairs_well_with": ["maven", "gradle", "docker"],
        "learning_tip": "Java projects usually depend on a build tool like Maven or Gradle for structure and repeatability.",
    },
    "go": {
        "label": "Go",
        "category": "language",
        "role": "A compiled language known for simple tooling and fast static binaries.",
        "pairs_well_with": ["git", "docker", "make"],
        "learning_tip": "Go has a very consistent project layout and tooling story, which is great for learners.",
    },
    "rustc": {
        "label": "Rust",
        "category": "language",
        "role": "A systems language focused on safety and performance.",
        "pairs_well_with": ["cargo", "git"],
        "learning_tip": "Rust's compiler messages are famously helpful when you're learning.",
    },
    "cargo": {
        "label": "Cargo",
        "category": "package-manager",
        "role": "Rust's build system and package manager.",
        "pairs_well_with": ["rustc"],
        "learning_tip": "Cargo handles project creation, dependency management, testing, and publishing.",
    },
    "pip": {
        "label": "pip",
        "category": "package-manager",
        "role": "Python's common package installer.",
        "pairs_well_with": ["python3", "venv"],
        "learning_tip": "If a project uses pip, also look for requirements files or a pyproject.toml.",
    },
    "uv": {
        "label": "uv",
        "category": "package-manager",
        "role": "A fast Python package and environment manager.",
        "pairs_well_with": ["python3", "pip", "venv"],
        "learning_tip": "uv can simplify Python setup by handling environments and installs in one workflow.",
    },
    "venv": {
        "label": "venv",
        "category": "environment",
        "role": "Python's built-in virtual environment tool.",
        "pairs_well_with": ["python3", "pip"],
        "learning_tip": "If you see a .venv folder, the project likely expects an isolated Python environment.",
    },
    "make": {
        "label": "Make",
        "category": "automation",
        "role": "Runs repeatable task recipes from a Makefile.",
        "pairs_well_with": ["git", "docker", "python3", "go"],
        "learning_tip": "Try `make help` when a repo includes a Makefile; it's often the quickest way to discover workflows.",
    },
}


STACK_PATTERNS = [
    {
        "id": "python-backend",
        "title": "Python App Stack",
        "requires": {"python3"},
        "signals": {"pip", "uv", "venv", "docker", "git"},
        "summary": "This environment is ready for Python scripting or backend application work.",
        "coaching": "A comfortable next step is learning how Python, package installation, and virtual environments fit together.",
    },
    {
        "id": "javascript-fullstack",
        "title": "JavaScript / TypeScript Stack",
        "requires": {"node"},
        "signals": {"npm", "pnpm", "git", "docker"},
        "summary": "This environment supports modern frontend tooling and Node-based development.",
        "coaching": "Newer frontend projects often combine Node, a package manager, and Git-driven workflows.",
    },
    {
        "id": "containerized-dev",
        "title": "Containerized Development",
        "requires": {"docker"},
        "signals": {"docker compose", "git", "python3", "node"},
        "summary": "Containers are part of this setup, which usually means reproducible local environments.",
        "coaching": "A helpful learning path is understanding images, containers, volumes, and multi-service compose files.",
    },
]


def describe_component(command_name: str) -> dict:
    """Return a normalized knowledge record for a command."""

    entry = COMPONENT_KNOWLEDGE.get(command_name, {})
    label = entry.get("label", command_name)
    return {
        "command": command_name,
        "label": label,
        "category": entry.get("category", "tool"),
        "role": entry.get(
            "role",
            f"{label} is installed on this machine, but it is not yet described in the built-in learning catalog.",
        ),
        "pairs_well_with": entry.get("pairs_well_with", []),
        "learning_tip": entry.get(
            "learning_tip",
            "Use this as a clue about the kind of projects this environment may be prepared to run.",
        ),
    }

