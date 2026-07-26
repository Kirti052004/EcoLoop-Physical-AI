"""
Quantitative Savings Dashboard Backend (FastAPI + WebSockets / REST API)
Provides real-time telemetry streaming, simulation controller triggers, and savings summary data endpoints.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from closed_loop_framework.closed_loop_controller import ClosedLoopController

app = FastAPI(
    title="Physical AI EcoLoop Building Controller Dashboard",
    description="Autonomous Cyber-Physical Building Management System Dashboard",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

controller = ClosedLoopController()
cached_simulation_results = None

@app.on_event("startup")
def startup_event():
    global cached_simulation_results
    try:
        cached_simulation_results = controller.run_pipeline()
    except Exception as e:
        print(f"Startup simulation exception: {e}")

@app.get("/api/simulation/run")
def run_simulation_endpoint():
    global cached_simulation_results
    try:
        cached_simulation_results = controller.run_pipeline()
        return {"status": "success", "summary": cached_simulation_results["summary"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/simulation/summary")
def get_summary_endpoint():
    global cached_simulation_results
    if not cached_simulation_results:
        cached_simulation_results = controller.run_pipeline()
    return cached_simulation_results["summary"]

@app.get("/api/simulation/telemetry")
def get_telemetry_endpoint():
    global cached_simulation_results
    if not cached_simulation_results:
        cached_simulation_results = controller.run_pipeline()
    return {
        "baseline": cached_simulation_results["baseline_telemetry"],
        "ai_ecoloop": cached_simulation_results["ai_telemetry"]
    }

@app.get("/api/simulation/control-logs")
def get_control_logs_endpoint():
    global cached_simulation_results
    if not cached_simulation_results:
        cached_simulation_results = controller.run_pipeline()
    return cached_simulation_results["control_logs"]

# Serve static frontend files
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../static"))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
