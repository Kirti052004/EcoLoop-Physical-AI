# EcoLoop Physical AI - Autonomous Smart Building Controller

> **Physical AI Proof-of-Concept (PoC)**: Closed-Loop Smart Building Energy & Carbon Automation using **EnergyPlus V26.1**, **Model Context Protocol (MCP)**, and **Open-Source LLMs**.

---

## 🌟 Executive Overview
Buildings account for ~40% of global energy consumption and a major share of operational carbon emissions. Traditional Building Management Systems (BMS) rely on static, rule-based schedules that fail to adapt dynamically to real-time changes in outdoor weather, occupancy shifts, and grid carbon emissions.

**EcoLoop Physical AI** pairs the **EnergyPlus physics simulation engine** with an **Open-Source LLM Cognitive Agent** via the **Model Context Protocol (MCP)** to form an automated closed-loop feedback pipeline:
1. **Feedback (EnergyPlus → AI)**: Real-time telemetry (zone temperatures, relative humidity, HVAC energy kW, ASHRAE 55 PMV thermal comfort index) streams continuously from EnergyPlus.
2. **Reasoning**: The AI model evaluates telemetry against dynamic grid carbon intensity ($gCO_2/kWh$), Time-Of-Use electricity pricing ($/kWh$), and human thermal comfort limits.
3. **Control Actions & Forward Injection (AI → EnergyPlus)**: Computes dynamic Energy Conservation Measures (ECMs) like thermal pre-cooling and carbon peak load shedding, injecting updated thermostat setpoints directly back into active EnergyPlus models (`building_models/ai_optimized_building.idf`).

---

## 📊 Quantifiable Savings Benchmark (7-Day EnergyPlus Run)

| Performance Metric | Baseline (Static Schedule) | EcoLoop Physical AI Agent | Net Savings / Improvement |
| :--- | :--- | :--- | :--- |
| **Total HVAC Energy (kWh)** | 133.38 kWh | 108.87 kWh | **-18.38% Energy Reduction** |
| **Operational Carbon ($kg CO_2$)** | 47.44 kg | 38.25 kg | **-19.36% Carbon Reduced** |
| **Total Energy Cost ($)** | $26.07 | $20.77 | **-20.36% Cost Saved** |
| **PMV Comfort Compliance (%)** | 35.7% | **69.8%** | **+34.1% Improved Comfort** |

---

## 🏗️ Repository Architecture & Deliverables

```
Eco-Loop Building Agents/
├── building_models/
│   ├── baseline_building.idf          # Base baseline EnergyPlus model
│   ├── ai_optimized_building.idf      # Modified version generated during evaluation
│   └── weather.epw                    # EnergyPlus weather dataset (San Francisco TMY3)
├── simulation_engine/
│   ├── energyplus_wrapper.py          # EnergyPlus API & subprocess wrapper
│   ├── pmv_calculator.py              # ASHRAE 55 Fanger PMV/PPD thermal comfort engine
│   └── grid_intensity_service.py      # Real-time grid carbon & tariff simulation service
├── cognitive_engine/
│   ├── mcp_server.py                  # Model Context Protocol (MCP) server & tool schemas
│   └── llm_agent.py                   # OSS LLM agent orchestration logic
├── closed_loop_framework/
│   └── closed_loop_controller.py      # Master feedback, reasoning & forward injection controller
├── dashboard/
│   ├── backend/
│   │   └── app.py                     # FastAPI server for telemetry API & dashboard
│   ├── static/
│   │   ├── index.html                 # Quantitative Savings Dashboard UI
│   │   ├── styles.css                 # Classic High-Contrast styling
│   │   └── app.js                     # Live chart renderer & decision timeline feed
├── docs/
│   ├── system_architecture.md         # System Architecture Document (Deliverable 4)
│   ├── presentation_deck.md           # Solution Presentation Deck (Deliverable 6)
│   └── poc_demonstration_video_script.md # 3-Minute PoC Video Script (Deliverable 5)
├── simulation_output/
│   ├── savings_summary.json           # Quantifiable savings summary JSON
│   └── savings_export.csv             # Comparative 672-timestep CSV dataset
└── run_poc.py                         # Master launcher script
```

---

## 🛠️ Model Context Protocol (MCP) Tools

The MCP Server (`cognitive_engine/mcp_server.py`) exposes 5 core tool APIs for the Open-Source LLM:
1. `get_building_telemetry()`: Returns real-time zone temperature, humidity, PMV index, and HVAC power.
2. `calculate_pmv_comfort(air_temp, rh, clo)`: Computes predicted ASHRAE 55 PMV thermal comfort.
3. `evaluate_grid_emissions(hour)`: Fetches current grid carbon intensity ($gCO_2/kWh$) and tariff ($/kWh$).
4. `apply_ecm_control_action(heating_setpoint, cooling_setpoint, ecm_strategy)`: Applies dynamic thermostat setpoints in EnergyPlus.
5. `parse_simulation_errors(err_log_content)`: Parses EnergyPlus `.err` logs for warnings and severe errors.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10+
- EnergyPlus V26.1 (Installed at `C:\EnergyPlusV26-1-0`)

### Installation & Execution

1. Clone the repository:
   ```bash
   git clone <YOUR_GITHUB_REPO_URL>
   cd Eco-Loop-Building-Agents
   ```

2. Install dependencies:
   ```bash
   pip install fastapi uvicorn requests pandas numpy eppy
   ```

3. Run the Physical AI Closed-Loop Controller & Dashboard:
   ```bash
   python run_poc.py
   ```

4. Open your browser at `http://127.0.0.1:8000` to view the live dashboard.

---

## 📜 License
MIT License.
