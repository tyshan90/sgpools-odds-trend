const state = {
  matches: [],
  selectedEventId: "",
  market: "1X2",
};

const colors = ["#146c5a", "#0f5f9c", "#b54708", "#6f5aa7", "#59636f"];

const el = {
  marketSelect: document.querySelector("#marketSelect"),
  refreshButton: document.querySelector("#refreshButton"),
  matchSearch: document.querySelector("#matchSearch"),
  matchList: document.querySelector("#matchList"),
  updatedText: document.querySelector("#updatedText"),
  competitionText: document.querySelector("#competitionText"),
  matchTitle: document.querySelector("#matchTitle"),
  snapshotCount: document.querySelector("#snapshotCount"),
  summaryGrid: document.querySelector("#summaryGrid"),
  chart: document.querySelector("#trendChart"),
  legend: document.querySelector("#legend"),
};

el.marketSelect.addEventListener("change", () => {
  state.market = el.marketSelect.value;
  loadMatches();
});
el.refreshButton.addEventListener("click", loadMatches);
el.matchSearch.addEventListener("input", renderMatchList);

loadMatches();

async function loadMatches() {
  setStatus("Loading snapshots");
  const response = await fetch(`/api/matches?market=${encodeURIComponent(state.market)}`);
  const payload = await response.json();
  state.matches = payload.matches || [];
  if (!state.matches.some((match) => match.event_id === state.selectedEventId)) {
    state.selectedEventId = state.matches[0]?.event_id || "";
  }
  renderMatchList();
  if (state.selectedEventId) {
    await loadTrend(state.selectedEventId);
  } else {
    renderEmptyTrend();
  }
}

function renderMatchList() {
  const query = el.matchSearch.value.trim().toLowerCase();
  const matches = state.matches.filter((match) => match.event_name.toLowerCase().includes(query));
  el.matchList.innerHTML = "";
  if (!matches.length) {
    el.matchList.innerHTML = `<div class="empty">No stored matches found.</div>`;
    return;
  }
  for (const match of matches) {
    const item = document.createElement("div");
    item.setAttribute("role", "listitem");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "match-item";
    if (match.event_id === state.selectedEventId) {
      button.setAttribute("aria-current", "true");
    }
    button.innerHTML = `
      <span class="match-name">${escapeHtml(match.event_name)}</span>
      <span class="match-meta">${escapeHtml(match.competition)} · ${match.snapshot_count} snapshots</span>
    `;
    button.addEventListener("click", () => {
      state.selectedEventId = match.event_id;
      renderMatchList();
      loadTrend(match.event_id);
    });
    item.appendChild(button);
    el.matchList.appendChild(item);
  }
}

async function loadTrend(eventId) {
  const response = await fetch(`/api/trend?event_id=${encodeURIComponent(eventId)}&market=${encodeURIComponent(state.market)}`);
  const trend = await response.json();
  renderTrend(trend);
}

function renderTrend(trend) {
  el.competitionText.textContent = [trend.category, trend.competition, trend.market_name].filter(Boolean).join(" · ");
  el.matchTitle.textContent = trend.event_name || "No match selected";
  const snapshots = Math.max(0, ...(trend.series || []).map((series) => series.points.length));
  el.snapshotCount.textContent = `${snapshots} snapshot${snapshots === 1 ? "" : "s"}`;
  setStatus(trend.series?.length ? `Latest snapshot: ${latestTimestamp(trend)}` : "No trend data available");
  renderSummary(trend.series || []);
  drawChart(trend.series || []);
  renderLegend(trend.series || []);
}

function renderSummary(seriesList) {
  el.summaryGrid.innerHTML = "";
  if (!seriesList.length) {
    el.summaryGrid.innerHTML = `<div class="empty">No trend points yet.</div>`;
    return;
  }
  for (const series of seriesList) {
    const first = series.points[0];
    const last = series.points[series.points.length - 1];
    const change = first && last ? last.decimal_odds - first.decimal_odds : 0;
    const percentChange = first?.decimal_odds ? (change / first.decimal_odds) * 100 : 0;
    const metric = document.createElement("div");
    metric.className = "metric";
    metric.innerHTML = `
      <div class="metric-label">${escapeHtml(series.selection_name)}</div>
      <div class="metric-value">${formatOdds(last?.decimal_odds)}</div>
      <div class="metric-change">${formatSignedPercent(percentChange)} from first snapshot</div>
    `;
    el.summaryGrid.appendChild(metric);
  }
}

function drawChart(seriesList) {
  const width = el.chart.clientWidth || 900;
  const height = el.chart.clientHeight || 420;
  const margin = { top: 24, right: 26, bottom: 46, left: 54 };
  const points = seriesList.flatMap((series) => series.points.map((point) => ({ ...point, time: Date.parse(point.captured_at) })));
  el.chart.setAttribute("viewBox", `0 0 ${width} ${height}`);
  el.chart.innerHTML = "";
  if (points.length < 1) {
    addText(width / 2, height / 2, "No trend data yet", "middle", "empty-text");
    return;
  }

  const minTime = Math.min(...points.map((point) => point.time));
  const maxTime = Math.max(...points.map((point) => point.time));
  const minOdds = Math.min(...points.map((point) => point.decimal_odds));
  const maxOdds = Math.max(...points.map((point) => point.decimal_odds));
  const oddsPad = Math.max(0.05, (maxOdds - minOdds) * 0.12);
  const yMin = Math.max(0, minOdds - oddsPad);
  const yMax = maxOdds + oddsPad;
  const plotW = width - margin.left - margin.right;
  const plotH = height - margin.top - margin.bottom;
  const xScale = (time) => margin.left + ((time - minTime) / Math.max(1, maxTime - minTime)) * plotW;
  const yScale = (odds) => margin.top + (1 - (odds - yMin) / Math.max(0.01, yMax - yMin)) * plotH;

  addGrid(width, height, margin, yMin, yMax, yScale);
  for (const [index, series] of seriesList.entries()) {
    const color = colors[index % colors.length];
    const pathData = series.points
      .map((point, pointIndex) => `${pointIndex === 0 ? "M" : "L"} ${xScale(Date.parse(point.captured_at)).toFixed(2)} ${yScale(point.decimal_odds).toFixed(2)}`)
      .join(" ");
    addPath(pathData, color);
    for (const point of series.points) {
      addCircle(xScale(Date.parse(point.captured_at)), yScale(point.decimal_odds), color);
    }
  }
  addText(margin.left, height - 14, new Date(minTime).toLocaleString(), "start", "axis-label");
  addText(width - margin.right, height - 14, new Date(maxTime).toLocaleString(), "end", "axis-label");
}

function addGrid(width, height, margin, yMin, yMax, yScale) {
  for (let i = 0; i <= 4; i += 1) {
    const value = yMin + ((yMax - yMin) * i) / 4;
    const y = yScale(value);
    addLine(margin.left, y, width - margin.right, y, "#e3e8ed");
    addText(margin.left - 10, y + 4, value.toFixed(2), "end", "axis-label");
  }
  addLine(margin.left, margin.top, margin.left, height - margin.bottom, "#b7c1cc");
  addLine(margin.left, height - margin.bottom, width - margin.right, height - margin.bottom, "#b7c1cc");
}

function renderLegend(seriesList) {
  el.legend.innerHTML = "";
  for (const [index, series] of seriesList.entries()) {
    const item = document.createElement("span");
    item.className = "legend-item";
    item.innerHTML = `<span class="swatch" style="background:${colors[index % colors.length]}"></span>${escapeHtml(series.selection_name)}`;
    el.legend.appendChild(item);
  }
}

function renderEmptyTrend() {
  el.matchTitle.textContent = "No match selected";
  el.competitionText.textContent = "No stored snapshots";
  el.snapshotCount.textContent = "0 snapshots";
  el.summaryGrid.innerHTML = `<div class="empty">Run the scraper to collect odds snapshots.</div>`;
  el.chart.innerHTML = "";
  el.legend.innerHTML = "";
  setStatus("No stored snapshots");
}

function addPath(d, color) {
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("d", d);
  path.setAttribute("fill", "none");
  path.setAttribute("stroke", color);
  path.setAttribute("stroke-width", "2.5");
  path.setAttribute("stroke-linecap", "round");
  path.setAttribute("stroke-linejoin", "round");
  el.chart.appendChild(path);
}

function addCircle(cx, cy, color) {
  const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  circle.setAttribute("cx", cx.toFixed(2));
  circle.setAttribute("cy", cy.toFixed(2));
  circle.setAttribute("r", "3.5");
  circle.setAttribute("fill", color);
  el.chart.appendChild(circle);
}

function addLine(x1, y1, x2, y2, color) {
  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  line.setAttribute("x1", x1.toFixed(2));
  line.setAttribute("y1", y1.toFixed(2));
  line.setAttribute("x2", x2.toFixed(2));
  line.setAttribute("y2", y2.toFixed(2));
  line.setAttribute("stroke", color);
  line.setAttribute("stroke-width", "1");
  el.chart.appendChild(line);
}

function addText(x, y, text, anchor, className) {
  const node = document.createElementNS("http://www.w3.org/2000/svg", "text");
  node.setAttribute("x", x.toFixed(2));
  node.setAttribute("y", y.toFixed(2));
  node.setAttribute("text-anchor", anchor);
  node.setAttribute("class", className);
  node.textContent = text;
  el.chart.appendChild(node);
}

function latestTimestamp(trend) {
  const values = trend.series.flatMap((series) => series.points.map((point) => point.captured_at));
  return values.sort().at(-1) || "";
}

function setStatus(text) {
  el.updatedText.textContent = text;
}

function formatOdds(value) {
  return typeof value === "number" ? value.toFixed(2) : "-";
}

function formatSigned(value) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}`;
}

function formatSignedPercent(value) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function escapeHtml(value) {
  return String(value || "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}
