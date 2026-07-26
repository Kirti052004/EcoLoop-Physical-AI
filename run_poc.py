"""
Physical AI EcoLoop Building Agent - Master System Launcher
Executes the closed-loop EnergyPlus simulation pipeline, generates deliverables, and launches the Quantitative Savings Dashboard.
"""

import os
import sys
import webbrowser

# Change working directory to project root automatically
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn
from closed_loop_framework.closed_loop_controller import ClosedLoopController
from dashboard.backend.app import app

def main():
    print("=" * 75)
    print("      PHYSICAL AI ECOLOOP AUTONOMOUS BUILDING AGENT LAUNCHER")
    print("=" * 75)
    print(f"Project Workspace: {PROJECT_ROOT}")
    print("EnergyPlus Engine: C:\\EnergyPlusV26-1-0\\energyplus.exe")
    print("-" * 75)

    print("\n[1/2] Initializing Closed-Loop Execution Pipeline...")
    controller = ClosedLoopController()
    results = controller.run_pipeline()

    print("\n=== QUANTITATIVE SAVINGS SUMMARY ===")
    summary = results["summary"]
    print(f"• HVAC Energy Savings  : -{summary['savings']['kwh_reduction_pct']}% ({summary['savings']['kwh_saved_total']} kWh saved)")
    print(f"• Carbon Footprint     : -{summary['savings']['carbon_reduction_pct']}% ({summary['savings']['carbon_saved_kg']} kg CO2 reduced)")
    print(f"• Operational Cost     : -{summary['savings']['cost_reduction_pct']}% (${summary['savings']['cost_saved_usd']} saved)")
    print(f"• Occupant PMV Comfort : {summary['ai_ecoloop']['pmv_comfort_compliance_pct']}% compliance (ASHRAE 55)")

    print("\n[2/2] Launching Executive Dashboard Server on http://127.0.0.1:8000...")
    
    # Open dashboard in default web browser
    webbrowser.open("http://127.0.0.1:8000")

    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
