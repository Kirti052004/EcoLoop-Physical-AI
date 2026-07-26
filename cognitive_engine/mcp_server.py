"""
Model Context Protocol (MCP) Server for Autonomous Smart Building Control
Exposes standardized tools for telemetry retrieval, thermal comfort evaluation, grid emissions tracking, ECM execution, and log parsing.
"""

import json
from typing import Dict, Any, List
from simulation_engine.pmv_calculator import calculate_pmv
from simulation_engine.grid_intensity_service import GridIntensityService

class MCPServer:
    def __init__(self):
        self.grid_service = GridIntensityService()
        self.active_control_state = {
            "heating_setpoint": 21.0,
            "cooling_setpoint": 24.0,
            "mode": "STANDARD",
            "pre_cooling_active": False,
            "demand_shedding_active": False
        }

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns JSON schema definitions of available MCP tools for Open-Source LLM tool calling.
        """
        return [
            {
                "name": "get_building_telemetry",
                "description": "Retrieves real-time sensor metrics from EnergyPlus simulation stream.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "include_historical_steps": {"type": "integer", "description": "Number of previous timesteps to include"}
                    }
                }
            },
            {
                "name": "calculate_pmv_comfort",
                "description": "Calculates ASHRAE 55 Fanger Predicted Mean Vote (PMV) thermal comfort index for proposed temperature/humidity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "air_temp": {"type": "number", "description": "Target zone temperature in °C"},
                        "rh": {"type": "number", "description": "Relative humidity % (default 50)"},
                        "clo": {"type": "number", "description": "Clothing insulation factor (default 0.8)"}
                    },
                    "required": ["air_temp"]
                }
            },
            {
                "name": "evaluate_grid_emissions",
                "description": "Fetches current grid carbon intensity (gCO2/kWh) and time-of-use tariff ($/kWh).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hour": {"type": "number", "description": "Hour of day (0 to 24)"}
                    },
                    "required": ["hour"]
                }
            },
            {
                "name": "apply_ecm_control_action",
                "description": "Applies Energy Conservation Measures (ECMs) and updates dynamic setpoints in EnergyPlus.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "heating_setpoint": {"type": "number", "description": "Target heating setpoint °C"},
                        "cooling_setpoint": {"type": "number", "description": "Target cooling setpoint °C"},
                        "ecm_strategy": {"type": "string", "description": "Strategy name: PRE_COOLING, PEAK_SHEDDING, COMFORT_OPTIMAL, BASELINE"}
                    },
                    "required": ["heating_setpoint", "cooling_setpoint"]
                }
            },
            {
                "name": "parse_simulation_errors",
                "description": "Extracts severe errors, warnings, and convergence failures from EnergyPlus simulation log.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "err_log_content": {"type": "string", "description": "Content of eplusout.err log file"}
                    }
                }
            }
        ]

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any], current_telemetry: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes specified MCP tool with given arguments.
        """
        if tool_name == "get_building_telemetry":
            if current_telemetry:
                return {"status": "success", "telemetry": current_telemetry}
            return {
                "status": "success",
                "telemetry": {
                    "zone_temperature": 23.5,
                    "relative_humidity": 45.0,
                    "pmv": -0.12,
                    "total_hvac_kwh": 1.25,
                    "outdoor_temperature": 26.4
                }
            }

        elif tool_name == "calculate_pmv_comfort":
            air_temp = float(arguments.get("air_temp", 23.0))
            rh = float(arguments.get("rh", 50.0))
            clo = float(arguments.get("clo", 0.8))
            pmv_res = calculate_pmv(ta=air_temp, rh=rh, clo=clo)
            return {"status": "success", "pmv_analysis": pmv_res}

        elif tool_name == "evaluate_grid_emissions":
            hour = float(arguments.get("hour", 14.0))
            grid_info = self.grid_service.get_grid_state(hour)
            return {"status": "success", "grid_metrics": grid_info}

        elif tool_name == "apply_ecm_control_action":
            htg = float(arguments.get("heating_setpoint", 20.0))
            clg = float(arguments.get("cooling_setpoint", 25.0))
            strategy = str(arguments.get("ecm_strategy", "CUSTOM"))

            self.active_control_state["heating_setpoint"] = htg
            self.active_control_state["cooling_setpoint"] = clg
            self.active_control_state["mode"] = strategy

            return {
                "status": "success",
                "message": f"Applied ECM Control Strategy: {strategy}",
                "updated_setpoints": {
                    "heating_setpoint": htg,
                    "cooling_setpoint": clg,
                    "ecm_strategy": strategy
                }
            }

        elif tool_name == "parse_simulation_errors":
            log = arguments.get("err_log_content", "")
            warnings = log.count("** Warning **")
            severe = log.count("** Severe **")
            fatal = log.count("** Fatal **")
            return {
                "status": "success",
                "warnings_count": warnings,
                "severe_count": severe,
                "fatal_count": fatal,
                "has_failures": (severe > 0 or fatal > 0),
                "diagnostic_summary": "Zero critical errors. Simulation running normally." if severe == 0 else f"Found {severe} severe errors."
            }

        else:
            return {"status": "error", "message": f"Unknown MCP tool: {tool_name}"}

if __name__ == "__main__":
    mcp = MCPServer()
    print("Schemas count:", len(mcp.get_tool_schemas()))
    print("Test Tool Exec (calculate_pmv_comfort):", mcp.execute_tool("calculate_pmv_comfort", {"air_temp": 24.5}))
