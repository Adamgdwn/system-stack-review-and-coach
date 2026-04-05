const statusText = document.querySelector("#statusText");
const summaryGrid = document.querySelector("#summaryGrid");
const environmentGrid = document.querySelector("#environmentGrid");
const componentGrid = document.querySelector("#componentGrid");
const stackMatches = document.querySelector("#stackMatches");
const learningPath = document.querySelector("#learningPath");
const recommendations = document.querySelector("#recommendations");
const commandLog = document.querySelector("#commandLog");
const runReviewButton = document.querySelector("#runReviewButton");
const shareSummaryButton = document.querySelector("#shareSummaryButton");
const runMapButton = document.querySelector("#runMapButton");
const suggestedRoots = document.querySelector("#suggestedRoots");
const customRootsInput = document.querySelector("#customRootsInput");
const mapSummaryGrid = document.querySelector("#mapSummaryGrid");
const mapTeachingNotes = document.querySelector("#mapTeachingNotes");
const configGrid = document.querySelector("#configGrid");
const scanResults = document.querySelector("#scanResults");
const componentTemplate = document.querySelector("#componentTemplate");
let currentReport = null;
let currentMap = null;

function setStatus(text) {
  statusText.textContent = text;
}

function renderSummary(report) {
  const breakdown = Object.entries(report.summary.category_breakdown)
    .map(([category, count]) => `${count} ${category}`)
    .join(" • ");

  summaryGrid.innerHTML = `
    <article class="summary-card">
      <span class="summary-label">Installed components</span>
      <strong>${report.summary.installed_component_count}</strong>
    </article>
    <article class="summary-card">
      <span class="summary-label">Detected mix</span>
      <strong>${breakdown || "No components found yet"}</strong>
    </article>
    <article class="summary-card">
      <span class="summary-label">Report generated</span>
      <strong>${new Date(report.generated_at).toLocaleString()}</strong>
    </article>
  `;
}

function renderEnvironment(report) {
  environmentGrid.innerHTML = "";
  Object.entries(report.environment).forEach(([key, value]) => {
    const card = document.createElement("article");
    card.className = "data-card";
    card.innerHTML = `<span>${key.replaceAll("_", " ")}</span><strong>${value}</strong>`;
    environmentGrid.appendChild(card);
  });
}

function renderComponents(report) {
  componentGrid.innerHTML = "";
  report.components.forEach((component) => {
    const fragment = componentTemplate.content.cloneNode(true);
    fragment.querySelector(".category").textContent = component.category;
    fragment.querySelector(".version").textContent = component.version || "Unknown version";
    fragment.querySelector(".title").textContent = component.label;
    fragment.querySelector(".role").textContent = component.role;
    fragment.querySelector(".path").textContent = component.path ? `Path: ${component.path}` : "Path unknown";
    fragment.querySelector(".tip").textContent = `Learning tip: ${component.learning_tip}`;
    const pairs = fragment.querySelector(".pairs");
    const pairText = component.pairs_well_with.length
      ? `Works well with: ${component.pairs_well_with.join(", ")}`
      : "No built-in pairing note yet.";
    pairs.textContent = pairText;
    componentGrid.appendChild(fragment);
  });
}

function renderStackMatches(report) {
  stackMatches.innerHTML = "";
  const matches = report.summary.primary_stack_matches;
  if (!matches.length) {
    stackMatches.innerHTML = `<article class="stack-card"><h3>Still learning the shape</h3><p>No strong stack pattern matched yet. That usually means the environment is minimal or highly specialized.</p></article>`;
    return;
  }
  matches.forEach((match) => {
    const item = document.createElement("article");
    item.className = "stack-card";
    item.innerHTML = `
      <div class="stack-topline">
        <h3>${match.title}</h3>
        <span class="pill confidence">${match.confidence} confidence</span>
      </div>
      <p>${match.summary}</p>
      <p>${match.coaching}</p>
    `;
    stackMatches.appendChild(item);
  });
}

function renderLearningPath(report) {
  learningPath.innerHTML = "";
  report.learning_path.forEach((step) => {
    const item = document.createElement("li");
    item.textContent = step;
    learningPath.appendChild(item);
  });
}

function renderRecommendations(report) {
  recommendations.innerHTML = "";
  report.recommendations.forEach((itemText) => {
    const item = document.createElement("li");
    item.textContent = itemText;
    recommendations.appendChild(item);
  });
}

function renderCommandLog(report) {
  commandLog.innerHTML = "";
  if (!report.command_log.length) {
    commandLog.textContent = "No commands were needed.";
    return;
  }
  report.command_log.forEach((entry) => {
    const line = document.createElement("div");
    line.className = "command-entry";
    line.innerHTML = `
      <code>${entry.command}</code>
      <span>exit ${entry.exit_code}</span>
      <span>${entry.duration_ms}ms</span>
      <p>${entry.output || "No output"}</p>
    `;
    commandLog.appendChild(line);
  });
}

function renderSuggestedRoots(payload) {
  suggestedRoots.innerHTML = "";
  payload.suggested_roots.forEach((root) => {
    const label = document.createElement("label");
    label.className = "chip-option";
    label.innerHTML = `
      <input type="checkbox" value="${root.path}" />
      <span>${root.path}</span>
    `;
    suggestedRoots.appendChild(label);
  });
}

function selectedRoots() {
  const checked = [...document.querySelectorAll("#suggestedRoots input:checked")].map((input) => input.value.trim());
  const manual = customRootsInput.value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
  return [...new Set([...checked, ...manual])];
}

function renderMapSummary(map) {
  mapSummaryGrid.innerHTML = `
    <article class="summary-card">
      <span class="summary-label">Roots scanned</span>
      <strong>${map.summary.roots_scanned}</strong>
    </article>
    <article class="summary-card">
      <span class="summary-label">Projects detected</span>
      <strong>${map.summary.projects_detected}</strong>
    </article>
    <article class="summary-card">
      <span class="summary-label">Configs detected</span>
      <strong>${map.summary.configs_detected}</strong>
    </article>
    <article class="summary-card">
      <span class="summary-label">Entries scanned</span>
      <strong>${map.summary.entries_scanned}</strong>
    </article>
  `;

  mapTeachingNotes.innerHTML = "";
  map.teaching_notes.forEach((note) => {
    const item = document.createElement("li");
    item.textContent = note;
    mapTeachingNotes.appendChild(item);
  });
}

function renderConfigFindings(map) {
  configGrid.innerHTML = "";
  if (!map.config_findings.length) {
    configGrid.innerHTML = `<article class="stack-card"><h3>No common config files found</h3><p>The selected roots did not expose any of the built-in config markers yet.</p></article>`;
    return;
  }
  map.config_findings.forEach((finding) => {
    const item = document.createElement("article");
    item.className = "stack-card";
    item.innerHTML = `<h3>${finding.label}</h3><p>${finding.path}</p><p>${finding.teaching}</p>`;
    configGrid.appendChild(item);
  });
}

function renderScanResults(map) {
  scanResults.innerHTML = "";
  if (!map.scans.length) {
    scanResults.innerHTML = `<article class="stack-card"><h3>No roots scanned yet</h3><p>Select one or more roots, then run a filesystem map.</p></article>`;
    return;
  }
  map.scans.forEach((scan) => {
    const projects = scan.projects.length
      ? scan.projects
          .map((project) => `<li><strong>${project.path}</strong><br>${project.types.join(", ")}<br>${project.teaching}</li>`)
          .join("")
      : "<li>No project markers found in this root.</li>";

    const dirs = scan.interesting_directories.length
      ? `<p><strong>Interesting directories:</strong> ${scan.interesting_directories.join(", ")}</p>`
      : "";

    const errors = scan.permission_errors.length
      ? `<p><strong>Permission limits:</strong> ${scan.permission_errors.join(", ")}</p>`
      : "";

    const card = document.createElement("article");
    card.className = "stack-card";
    card.innerHTML = `
      <div class="stack-topline">
        <h3>${scan.root}</h3>
        <span class="pill">${scan.summary.projects_detected} projects</span>
      </div>
      <p>Scanned ${scan.summary.entries_scanned} entries, including ${scan.summary.directories} directories and ${scan.summary.files} files.</p>
      ${dirs}
      ${errors}
      <ul class="text-list compact-list">${projects}</ul>
    `;
    scanResults.appendChild(card);
  });
}

async function loadScanOptions() {
  const response = await fetch("/api/scan-options", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Scan options failed with status ${response.status}`);
  }
  renderSuggestedRoots(await response.json());
}

async function runMap() {
  const roots = selectedRoots();
  if (!roots.length) {
    setStatus("Choose at least one root before running a filesystem map.");
    return;
  }
  setStatus("Scanning the selected roots locally...");
  runMapButton.disabled = true;
  try {
    const response = await fetch("/api/map", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roots }),
    });
    if (!response.ok) {
      throw new Error(`Map request failed with status ${response.status}`);
    }
    currentMap = await response.json();
    renderMapSummary(currentMap);
    renderConfigFindings(currentMap);
    renderScanResults(currentMap);
    setStatus("Filesystem map complete. Review the discovered roots, projects, and configs below.");
  } catch (error) {
    console.error(error);
    setStatus(`Filesystem map failed: ${error.message}`);
  } finally {
    runMapButton.disabled = false;
  }
}

async function copyShareSummary() {
  if (!currentReport) {
    setStatus("Run a local review before copying a share summary.");
    return;
  }

  const lines = [
    "System Stack Review and Coach",
    "",
    `Generated: ${new Date(currentReport.generated_at).toLocaleString()}`,
    `Operating system: ${currentReport.environment.os}`,
    `Shell: ${currentReport.environment.shell}`,
    `Installed components: ${currentReport.summary.installed_component_count}`,
    "Detected tools:",
    ...currentReport.components.slice(0, 18).map((component) => `- ${component.label} (${component.category})`),
  ];

  if (currentMap) {
    lines.push("");
    lines.push(`Roots scanned: ${currentMap.summary.roots_scanned}`);
    lines.push(`Projects detected: ${currentMap.summary.projects_detected}`);
    lines.push(`Configs detected: ${currentMap.summary.configs_detected}`);
  }

  lines.push("");
  lines.push("Generated locally on this machine.");
  const summary = lines.join("\n");

  try {
    await navigator.clipboard.writeText(summary);
    setStatus("Share summary copied to the clipboard.");
  } catch (error) {
    console.error(error);
    setStatus("Clipboard copy failed in this browser session.");
  }
}

async function runReview() {
  setStatus("Running local probe agents...");
  runReviewButton.disabled = true;
  try {
    const response = await fetch("/api/report", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }
    const report = await response.json();
    currentReport = report;
    renderSummary(report);
    renderEnvironment(report);
    renderComponents(report);
    renderStackMatches(report);
    renderLearningPath(report);
    renderRecommendations(report);
    renderCommandLog(report);
    setStatus("Review complete. Explore the sections below to learn the environment.");
  } catch (error) {
    console.error(error);
    setStatus(`Review failed: ${error.message}`);
  } finally {
    runReviewButton.disabled = false;
  }
}

runMapButton.addEventListener("click", runMap);
shareSummaryButton.addEventListener("click", copyShareSummary);
runReviewButton.addEventListener("click", runReview);
loadScanOptions().catch((error) => {
  console.error(error);
  setStatus(`Could not load scan options: ${error.message}`);
});
runReview();
