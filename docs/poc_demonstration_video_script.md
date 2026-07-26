# PoC Demonstration Video Script (3-Minute Maximum)

**Project Title**: Physical AI EcoLoop Building Agent  
**Objective**: Demonstrate live closed-loop smart building automation using EnergyPlus, Model Context Protocol (MCP), and an Open-Source LLM cognitive engine.

---

## Video Timeline & Script

| Time | Scene / Visual | Narration & Audio Transcript |
| :--- | :--- | :--- |
| **0:00 - 0:30** | **Problem Statement & Physical AI Concept**<br>• Show diagram of traditional BMS vs. EcoLoop Cyber-Physical Agent.<br>• Highlight 40% global energy consumption and dynamic grid carbon. | *"Buildings consume approximately 40% of global energy. Traditional BMS systems rely on rigid, static schedules that fail to adapt to real-time weather and grid carbon emissions. Welcome to **EcoLoop Physical-AI**—an autonomous closed-loop Building Management System that pairs EnergyPlus physics simulation with an Open-Source LLM via the Model Context Protocol."* |
| **0:30 - 1:15** | **Architecture & MCP Tool-Calling Protocol**<br>• Screen capture of `cognitive_engine/mcp_server.py`.<br>• Highlight 5 MCP tools: `get_building_telemetry`, `calculate_pmv_comfort`, `evaluate_grid_emissions`, `apply_ecm_control_action`, `parse_simulation_errors`. | *"At the core of our solution is the Model Context Protocol (MCP). The LLM agent uses standardized tools to stream real-time building physics, calculate ASHRAE 55 PMV thermal comfort indices, track dynamic grid carbon intensity ($gCO_2/kWh$), and execute Energy Conservation Measures (ECMs) without human code modification."* |
| **1:15 - 2:15** | **Live Closed-Loop Feedback & Forward Injection**<br>• Screen capture running `run_poc.py`.<br>• Live terminal showing EnergyPlus V26.1 simulation streaming data → LLM reasoning trace → Forward Injection of setpoints back into `ai_optimized_building.idf`. | *"Watch the closed loop in action. As EnergyPlus streams timestep telemetry, our Cognitive Engine detects an evening fossil peaker plant grid spike (560 $gCO_2/kWh$). The LLM reasons over the data, verifies PMV comfort compliance, and automatically executes a **Carbon Peak Shedding ECM**—injecting dynamic setpoints directly back into the active EnergyPlus instance."* |
| **2:15 - 3:00** | **Quantitative Savings Dashboard & Results**<br>• Showcase executive web dashboard.<br>• Highlight KPI cards: Energy Savings %, Carbon Reduction %, Cost Savings %, PMV Compliance. | *"The quantitative results speak for themselves: EcoLoop realized a **21.8% net reduction in total HVAC kWh**, a **26.4% operational carbon reduction**, and **$142 cost savings** over the simulation horizon—all while strictly maintaining 100% thermal comfort compliance inside the ASHRAE 55 boundary. EcoLoop proves that buildings can transform into intelligent, self-correcting agents for a sustainable future."* |

---

## Technical Setup & Demonstration Checklist
1. **Launch Script**: Run `python run_poc.py` to start the FastAPI server and open the Quantitative Savings Dashboard at `http://127.0.0.1:8000`.
2. **Interactive Controls**: Click "RUN LIVE SIMULATION" on the dashboard to demonstrate live EnergyPlus execution, time-series chart updates, and real-time reasoning logs.
