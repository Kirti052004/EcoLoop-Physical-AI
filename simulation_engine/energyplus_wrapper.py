"""
EnergyPlus API & Subprocess Wrapper
Manages EnergyPlus execution, IDF schedule/setpoint modifications, output parsing, and error extraction.
"""

import os
import re
import subprocess
import pandas as pd
from typing import Dict, List, Any

class EnergyPlusWrapper:
    def __init__(self, energyplus_dir: str = r"C:\EnergyPlusV26-1-0"):
        self.ep_dir = energyplus_dir
        self.ep_exe = os.path.join(energyplus_dir, "energyplus.exe")
        self.readvars_exe = os.path.join(energyplus_dir, "PostProcess", "ReadVarsESO.exe")
        
        if not os.path.exists(self.ep_exe):
            raise FileNotFoundError(f"EnergyPlus executable not found at: {self.ep_exe}")

    def modify_idf_setpoints(self, base_idf_path: str, target_idf_path: str, heating_setpoint: float, cooling_setpoint: float) -> str:
        """
        Dynamically generates a modified EnergyPlus IDF file with updated heating/cooling setpoints.
        """
        with open(base_idf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Update Baseline Heating Setpoint Schedule value
        content = re.sub(
            r'(Schedule:Compact,\s*Baseline Heating Setpoint Schedule,.*?Until: 24:00,\s*)[\d\.]+',
            rf'\g<1>{heating_setpoint:.1f}',
            content,
            flags=re.DOTALL
        )

        # Update Baseline Cooling Setpoint Schedule value
        content = re.sub(
            r'(Schedule:Compact,\s*Baseline Cooling Setpoint Schedule,.*?Until: 24:00,\s*)[\d\.]+',
            rf'\g<1>{cooling_setpoint:.1f}',
            content,
            flags=re.DOTALL
        )

        with open(target_idf_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return target_idf_path

    def run_simulation(self, idf_path: str, weather_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Executes EnergyPlus simulation, runs ReadVarsESO to generate CSV, and returns execution status.
        """
        os.makedirs(output_dir, exist_ok=True)
        abs_output_dir = os.path.abspath(output_dir)
        abs_idf = os.path.abspath(idf_path)
        abs_weather = os.path.abspath(weather_path)

        cmd = [
            self.ep_exe,
            "--weather", abs_weather,
            "--output-directory", abs_output_dir,
            abs_idf
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        success = result.returncode == 0
        
        # Post-process ESO file to CSV if ReadVarsESO exists
        eso_file = os.path.join(abs_output_dir, "eplusout.eso")
        csv_file = os.path.join(abs_output_dir, "eplusout.csv")

        if os.path.exists(eso_file) and os.path.exists(self.readvars_exe):
            subprocess.run([self.readvars_exe], cwd=abs_output_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        err_file = os.path.join(abs_output_dir, "eplusout.err")
        diagnostics = self.parse_error_log(err_file)

        return {
            "success": success,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "csv_file": csv_file if os.path.exists(csv_file) else None,
            "err_file": err_file if os.path.exists(err_file) else None,
            "diagnostics": diagnostics
        }

    def parse_error_log(self, err_file_path: str) -> Dict[str, Any]:
        """
        Parses EnergyPlus .err log file for severe errors, warnings, and convergence status.
        """
        if not err_file_path or not os.path.exists(err_file_path):
            return {"warnings_count": 0, "severe_count": 0, "errors": []}

        warnings = 0
        severe = 0
        error_lines = []

        with open(err_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if "** Warning **" in line:
                    warnings += 1
                elif "** Severe **" in line or "** Fatal **" in line:
                    severe += 1
                    error_lines.append(line.strip())

        return {
            "warnings_count": warnings,
            "severe_count": severe,
            "errors": error_lines
        }

    def parse_simulation_telemetry(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """
        Parses output variables from eplusout.csv into time-step telemetry dictionary records.
        """
        if not csv_file_path or not os.path.exists(csv_file_path):
            return []

        df = pd.read_csv(csv_file_path)
        df.columns = [c.strip() for c in df.columns]

        telemetry = []
        for idx, row in df.iterrows():
            temp_col = [c for c in df.columns if "Zone Mean Air Temperature" in c]
            rh_col = [c for c in df.columns if "Zone Air Relative Humidity" in c]
            pmv_col = [c for c in df.columns if "Fanger Model PMV" in c]
            clg_col = [c for c in df.columns if "Cooling Energy" in c]
            htg_col = [c for c in df.columns if "Heating Energy" in c]
            out_col = [c for c in df.columns if "Outdoor Air Drybulb Temperature" in c]

            zone_temp = float(row[temp_col[0]]) if temp_col else 22.0
            rh = float(row[rh_col[0]]) if rh_col else 50.0
            pmv = float(row[pmv_col[0]]) if pmv_col else 0.0
            cooling_j = float(row[clg_col[0]]) if clg_col else 0.0
            heating_j = float(row[htg_col[0]]) if htg_col else 0.0
            outdoor_temp = float(row[out_col[0]]) if out_col else 20.0

            cooling_kwh = cooling_j / 3600000.0
            heating_kwh = heating_j / 3600000.0
            total_hvac_kwh = cooling_kwh + heating_kwh

            date_str = str(row.get("Date/Time", f"Step {idx}")).strip()

            # Extract hour of day from "07/01 14:15:00"
            hour = 12.0
            try:
                parts = date_str.split()
                if len(parts) >= 2:
                    time_parts = parts[1].split(':')
                    hour = float(time_parts[0]) + float(time_parts[1]) / 60.0
            except Exception:
                hour = (idx % 24) * 1.0

            telemetry.append({
                "step": idx,
                "date_time": date_str,
                "hour": round(hour, 2),
                "zone_temperature": round(zone_temp, 2),
                "relative_humidity": round(rh, 1),
                "pmv": round(pmv, 3),
                "outdoor_temperature": round(outdoor_temp, 2),
                "cooling_kwh": round(cooling_kwh, 4),
                "heating_kwh": round(heating_kwh, 4),
                "total_hvac_kwh": round(total_hvac_kwh, 4)
            })

        return telemetry

if __name__ == "__main__":
    wrapper = EnergyPlusWrapper()
    res = wrapper.run_simulation(
        idf_path=r"building_models/baseline_building.idf",
        weather_path=r"building_models/weather.epw",
        output_dir=r"test_out"
    )
    print("Simulation execution status:", res["success"])
    telemetry = wrapper.parse_simulation_telemetry(res["csv_file"])
    print(f"Parsed {len(telemetry)} telemetry records.")
    print("First Telemetry record:", telemetry[0])
