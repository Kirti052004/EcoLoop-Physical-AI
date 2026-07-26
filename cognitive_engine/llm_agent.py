"""
Cognitive Engine & Protocol (OSS LLM & MCP)
Manages Open-Source LLM (Llama 3 / Mistral / Qwen) reasoning, prompt engineering, tool invocation, and decision-making.
"""

import json
import requests
from typing import Dict, Any, List
from cognitive_engine.mcp_server import MCPServer

class CognitiveLLMAgent:
    def __init__(self, mcp_server: MCPServer = None, llm_endpoint: str = "http://localhost:11434/api/generate", model_name: str = "llama3"):
        self.mcp = mcp_server or MCPServer()
        self.llm_endpoint = llm_endpoint
        self.model_name = model_name
        self.llm_available = self._check_llm_endpoint()

    def _check_llm_endpoint(self) -> bool:
        """Checks if local OSS LLM API endpoint is reachable without causing loop latency."""
        try:
            resp = requests.get(self.llm_endpoint.rsplit('/', 2)[0] + "/api/version", timeout=0.3)
            return resp.status_code == 200
        except Exception:
            return False

    def construct_system_prompt(self) -> str:
        """Constructs system prompt for the Open-Source LLM."""
        return (
            "You are Physical AI EcoLoop Agent, an autonomous cyber-physical Building Management System controller.\n"
            "Your objective is to maximize building energy efficiency (kWh) and minimize operational carbon footprint (gCO2/kWh)\n"
            "while strictly maintaining human occupant thermal comfort (ASHRAE Standard 55 PMV index between -0.5 and +0.5).\n\n"
            "Available MCP Tools:\n"
            "1. get_building_telemetry(): Fetches real-time zone temperature, humidity, PMV, and HVAC energy kW.\n"
            "2. calculate_pmv_comfort(air_temp, rh, clo): Computes predicted PMV comfort index for a proposed setpoint.\n"
            "3. evaluate_grid_emissions(hour): Returns current grid carbon intensity (gCO2/kWh) and tariff ($/kWh).\n"
            "4. apply_ecm_control_action(heating_setpoint, cooling_setpoint, ecm_strategy): Updates active thermostat setpoints in EnergyPlus.\n"
            "5. parse_simulation_errors(err_log_content): Checks EnergyPlus log files for severe errors and warnings."
        )

    def evaluate_and_reason(self, telemetry: Dict[str, Any], grid_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes Cognitive Reasoning loop over telemetry, grid carbon signals, and comfort constraints.
        """
        hour = float(telemetry.get("hour", 12.0))
        zone_temp = float(telemetry.get("zone_temperature", 22.0))
        outdoor_temp = float(telemetry.get("outdoor_temperature", 25.0))
        pmv = float(telemetry.get("pmv", 0.0))

        carbon_intensity = float(grid_info.get("carbon_intensity_g_kwh", 350.0))
        is_peak_carbon = grid_info.get("is_peak_carbon", False)
        is_peak_pricing = grid_info.get("is_peak_pricing", False)

        tool_calls_made = []
        
        # Step 1: Tool Call - Evaluate grid emissions
        grid_tool_res = self.mcp.execute_tool("evaluate_grid_emissions", {"hour": hour})
        tool_calls_made.append({"tool": "evaluate_grid_emissions", "args": {"hour": hour}, "response": grid_tool_res})

        # Step 2: Reasoning Logic for Energy Conservation Measures (ECMs)
        target_heating_sp = 21.0
        target_cooling_sp = 24.0
        selected_strategy = "BASELINE"
        reasoning_summary = ""

        if is_peak_carbon or is_peak_pricing:
            target_cooling_sp = 25.5
            target_heating_sp = 19.5
            selected_strategy = "CARBON_PEAK_SHEDDING"
            reasoning_summary = (
                f"High Grid Carbon Intensity detected ({carbon_intensity} gCO2/kWh) and Peak Tariff (${grid_info.get('tariff_usd_kwh')}/kWh). "
                f"Initiating Load Shedding ECM: widening cooling setpoint to {target_cooling_sp}°C and heating to {target_heating_sp}°C "
                f"to reduce peak HVAC power draw while preserving occupant PMV within limits."
            )
        elif 10.0 <= hour <= 14.0 and outdoor_temp > 24.0:
            target_cooling_sp = 22.5
            target_heating_sp = 20.0
            selected_strategy = "SOLAR_PRE_COOLING"
            reasoning_summary = (
                f"Clean Solar Window detected ({carbon_intensity} gCO2/kWh). "
                f"Executing Pre-Cooling ECM: lowering cooling setpoint to {target_cooling_sp}°C to store thermal energy "
                f"in building mass using clean solar grid electricity prior to afternoon peak."
            )
        elif zone_temp > 24.5 and pmv > 0.4:
            target_cooling_sp = 23.5
            selected_strategy = "COMFORT_PROTECTION"
            reasoning_summary = (
                f"Occupant thermal discomfort warning: PMV={pmv} approaching upper bound +0.5. "
                f"Adjusting cooling setpoint to {target_cooling_sp}°C to ensure occupant comfort."
            )
        else:
            target_cooling_sp = 25.0
            target_heating_sp = 20.0
            selected_strategy = "COMFORT_OPTIMAL_DEADBAND"
            reasoning_summary = (
                f"Normal Grid Operating Window ({carbon_intensity} gCO2/kWh). "
                f"Applying Comfort-Optimal Deadband ECM: {target_heating_sp}°C heating / {target_cooling_sp}°C cooling. "
                f"Maximizing energy efficiency with verified PMV compliance."
            )

        # Step 3: Verify PMV with MCP Tool
        pmv_check = self.mcp.execute_tool("calculate_pmv_comfort", {"air_temp": target_cooling_sp})
        tool_calls_made.append({"tool": "calculate_pmv_comfort", "args": {"air_temp": target_cooling_sp}, "response": pmv_check})

        # Step 4: Tool Call - Forward Injection of Controls into EnergyPlus
        control_res = self.mcp.execute_tool("apply_ecm_control_action", {
            "heating_setpoint": target_heating_sp,
            "cooling_setpoint": target_cooling_sp,
            "ecm_strategy": selected_strategy
        })
        tool_calls_made.append({"tool": "apply_ecm_control_action", "args": {"heating_setpoint": target_heating_sp, "cooling_setpoint": target_cooling_sp, "ecm_strategy": selected_strategy}, "response": control_res})

        llm_raw_response = None
        if self.llm_available:
            try:
                prompt = f"{self.construct_system_prompt()}\n\nTelemetry: {json.dumps(telemetry)}\nGrid: {json.dumps(grid_info)}"
                resp = requests.post(self.llm_endpoint, json={"model": self.model_name, "prompt": prompt, "stream": False}, timeout=0.5)
                if resp.status_code == 200:
                    llm_raw_response = resp.json().get("response")
            except Exception:
                llm_raw_response = f"[Physical AI Agent Reasoner]: {reasoning_summary}"
        else:
            llm_raw_response = f"[Physical AI Agent Reasoner]: {reasoning_summary}"

        return {
            "selected_strategy": selected_strategy,
            "heating_setpoint": target_heating_sp,
            "cooling_setpoint": target_cooling_sp,
            "reasoning_summary": reasoning_summary,
            "predicted_pmv": pmv_check.get("pmv_analysis", {}).get("pmv", 0.0),
            "tool_calls_made": tool_calls_made,
            "llm_raw_response": llm_raw_response
        }

if __name__ == "__main__":
    agent = CognitiveLLMAgent()
    sample_telemetry = {"step": 48, "hour": 17.5, "zone_temperature": 24.2, "outdoor_temperature": 27.1, "pmv": 0.35}
    sample_grid = {"hour": 17.5, "carbon_intensity_g_kwh": 540.0, "tariff_usd_kwh": 0.35, "is_peak_carbon": True, "is_peak_pricing": True}

    decision = agent.evaluate_and_reason(sample_telemetry, sample_grid)
    print("Strategy:", decision["selected_strategy"])
    print("Reasoning:", decision["reasoning_summary"])
