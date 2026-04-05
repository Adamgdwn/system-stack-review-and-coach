#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
launcher="${repo_root}/launchers/run-stack-coach.sh"
desktop_dir="${HOME}/Desktop"
applications_dir="${HOME}/.local/share/applications"
desktop_file="${applications_dir}/system-stack-review-and-coach.desktop"
desktop_copy="${desktop_dir}/System Stack Review and Coach.desktop"
icon="utilities-terminal"

mkdir -p "${applications_dir}" "${desktop_dir}"

cat > "${desktop_file}" <<EOF
[Desktop Entry]
Type=Application
Name=System Stack Review and Coach
Comment=Learn the local development stack through guided local reviews
Exec=${launcher}
Path=${repo_root}
Terminal=false
Categories=Development;Education;
Icon=${icon}
StartupNotify=true
EOF

cp "${desktop_file}" "${desktop_copy}"
chmod +x "${desktop_file}" "${desktop_copy}" "${launcher}"

if command -v gio >/dev/null 2>&1; then
  gio set "${desktop_copy}" metadata::trusted true >/dev/null 2>&1 || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "${applications_dir}" >/dev/null 2>&1 || true
fi

echo "Installed desktop launcher:"
echo "  ${desktop_file}"
echo "  ${desktop_copy}"
