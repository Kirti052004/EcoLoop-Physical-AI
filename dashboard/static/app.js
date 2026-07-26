// EcoLoop Smart Building Agent Application Logic

let energyChart = null;
let comfortChart = null;

document.addEventListener("DOMContentLoaded", () => {
  fetchDashboardData();
});

async function fetchDashboardData() {
  try {
    const summaryRes = await fetch("/api/simulation/summary");
    const summary = await summaryRes.json();
    updateKPICards(summary);

    const telemetryRes = await fetch("/api/simulation/telemetry");
    const telemetryData = await telemetryRes.json();
    renderCharts(telemetryData.baseline, telemetryData.ai_ecoloop);
    renderTelemetryTable(telemetryData.baseline, telemetryData.ai_ecoloop);

    const logsRes = await fetch("/api/simulation/control-logs");
    const logs = await logsRes.json();
    renderActionFeed(logs);
  } catch (err) {
    console.error("Error loading simulation dashboard data:", err);
  }
}

function updateKPICards(summary) {
  if (!summary || !summary.savings) return;

  const s = summary.savings;
  const ai = summary.ai_ecoloop;

  document.getElementById("kwh-pct-val").innerText = `-${s.kwh_reduction_pct}%`;
  document.getElementById("kwh-total-val").innerText = `-${s.kwh_saved_total} kWh Saved`;

  document.getElementById("carbon-pct-val").innerText = `-${s.carbon_reduction_pct}%`;
  document.getElementById("carbon-total-val").innerText = `-${s.carbon_saved_kg} kg CO₂`;

  document.getElementById("cost-pct-val").innerText = `-${s.cost_reduction_pct}%`;
  document.getElementById("cost-total-val").innerText = `-$${s.cost_saved_usd} Saved`;

  document.getElementById("comfort-score-val").innerText = `${ai.pmv_comfort_compliance_pct}%`;
}

function renderCharts(baseline, ai) {
  const labels = baseline.slice(0, 48).map(d => (d.date_time.split(" ")[1] || `Step ${d.step}`).substring(0, 5));
  const baseKwh = baseline.slice(0, 48).map(d => d.total_hvac_kwh);
  const aiKwh = ai.slice(0, 48).map(d => d.total_hvac_kwh);

  const basePmv = baseline.slice(0, 48).map(d => d.pmv);
  const aiPmv = ai.slice(0, 48).map(d => d.pmv);

  // 1. Electricity Usage Chart
  const ctx1 = document.getElementById("energyChart").getContext("2d");
  if (energyChart) energyChart.destroy();
  
  energyChart = new Chart(ctx1, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Fixed Schedule (kW)",
          data: baseKwh,
          borderColor: "#1B3B2B", // Deep Forest Pine
          borderWidth: 2.5,
          pointRadius: 0,
          tension: 0.2
        },
        {
          label: "Smart AI Agent (kW)",
          data: aiKwh,
          borderColor: "#C85A32", // Terracotta Coral
          backgroundColor: "rgba(200, 90, 50, 0.12)",
          borderWidth: 3,
          fill: true,
          pointRadius: 3,
          tension: 0.2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: "#D3CBC0" }, ticks: { color: "#1B3B2B", font: { family: "Arial", size: 11, weight: "bold" } } },
        y: { grid: { color: "#D3CBC0" }, ticks: { color: "#1B3B2B", font: { family: "Arial", size: 11, weight: "bold" } }, title: { display: true, text: "Power (kW)", color: "#1B3B2B", font: { family: "Times New Roman", size: 13, weight: "bold" } } }
      },
      plugins: { legend: { labels: { color: "#1B3B2B", font: { family: "Arial", size: 11, weight: "bold" } } } }
    }
  });

  // 2. Room Comfort Chart
  const ctx2 = document.getElementById("comfortChart").getContext("2d");
  if (comfortChart) comfortChart.destroy();

  comfortChart = new Chart(ctx2, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Fixed Schedule Comfort",
          data: basePmv,
          borderColor: "#7A8C80",
          borderWidth: 1.5,
          pointRadius: 0
        },
        {
          label: "Smart AI Comfort",
          data: aiPmv,
          borderColor: "#2E6B52", // Sage Green
          borderWidth: 2.5,
          pointRadius: 2
        },
        {
          label: "Upper Target (+0.5)",
          data: Array(labels.length).fill(0.5),
          borderColor: "#C85A32",
          borderDash: [4, 4],
          pointRadius: 0
        },
        {
          label: "Lower Target (-0.5)",
          data: Array(labels.length).fill(-0.5),
          borderColor: "#C85A32",
          borderDash: [4, 4],
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { grid: { color: "#D3CBC0" }, ticks: { color: "#1B3B2B", font: { family: "Arial", size: 11, weight: "bold" } } },
        y: { min: -1.0, max: 1.0, grid: { color: "#D3CBC0" }, ticks: { color: "#1B3B2B", font: { family: "Arial", size: 11, weight: "bold" } }, title: { display: true, text: "Comfort Index (PMV)", color: "#1B3B2B", font: { family: "Times New Roman", size: 13, weight: "bold" } } }
      },
      plugins: { legend: { labels: { color: "#1B3B2B", font: { family: "Arial", size: 11, weight: "bold" } } } }
    }
  });
}

function renderActionFeed(logs) {
  const container = document.getElementById("feed-timeline");
  container.innerHTML = "";

  const displayLogs = logs.slice(0, 10);
  displayLogs.forEach((log, idx) => {
    const timeStr = log.date_time.split(" ")[1] || `Step ${log.step}`;
    const timeShort = timeStr.substring(0, 5);

    let sensorText = `Solar heat load increase (+2.1°C)`;
    let actionText = `Pre-cooling setpoint to ${log.cooling_setpoint}°C`;
    let impactText = `Storing cool air before peak electricity rates`;

    if (log.selected_strategy === "CARBON_PEAK_SHEDDING") {
      sensorText = `Fossil peaker power grid spike (${log.grid_carbon_g_kwh} gCO₂/kWh)`;
      actionText = `Adjusting cooling setpoint to ${log.cooling_setpoint}°C`;
      impactText = `Shedding expensive peak electricity and carbon emissions`;
    } else if (log.selected_strategy === "SOLAR_PRE_COOLING") {
      sensorText = `High clean solar electricity window`;
      actionText = `Pre-cooling room to ${log.cooling_setpoint}°C`;
      impactText = `Storing thermal mass using clean solar energy`;
    } else if (log.selected_strategy === "COMFORT_PROTECTION") {
      sensorText = `Room temperature approaching discomfort limit`;
      actionText = `Adjusting cooling setpoint to ${log.cooling_setpoint}°C`;
      impactText = `Ensuring healthy occupant room comfort`;
    }

    const isAlert = log.selected_strategy === "CARBON_PEAK_SHEDDING" || log.selected_strategy === "COMFORT_PROTECTION";

    const div = document.createElement("div");
    div.className = `feed-item ${isAlert ? 'alert' : ''}`;
    div.innerHTML = `
      <span class="feed-time">[${timeShort}]</span>
      <span class="feed-tag-sensor">Sensor: ${sensorText}</span>
      <strong>-&gt;</strong> <span class="feed-tag-action">AI Action: ${actionText}</span>
      <strong>-&gt;</strong> <span class="feed-tag-impact">Impact: ${impactText}</span>
    `;
    container.appendChild(div);
  });
}

function renderTelemetryTable(baseline, ai) {
  const tbody = document.getElementById("telemetry-tbody");
  tbody.innerHTML = "";

  const rowsToShow = baseline.slice(0, 8);
  rowsToShow.forEach((b, idx) => {
    const a = ai[idx];
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${b.date_time}</strong></td>
      <td>${b.outdoor_temperature}°C</td>
      <td>${b.zone_temperature}°C</td>
      <td><strong style="color:var(--accent-sage)">${a.zone_temperature}°C</strong></td>
      <td>${a.carbon_intensity_g_kwh} gCO₂</td>
      <td>${b.total_hvac_kwh} kW</td>
      <td><strong style="color:var(--accent-terracotta)">${a.total_hvac_kwh} kW</strong></td>
      <td><span class="brand-badge" style="font-size:0.7rem">${a.strategy}</span></td>
    `;
    tbody.appendChild(tr);
  });
}

async function triggerSimulationRun() {
  const btn = document.querySelector(".btn-run");
  btn.innerText = "SIMULATING ENERGYPLUS...";
  btn.disabled = true;
  await fetch("/api/simulation/run");
  await fetchDashboardData();
  btn.innerText = "RUN LIVE SIMULATION";
  btn.disabled = false;
}
