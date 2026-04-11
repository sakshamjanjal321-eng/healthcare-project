"""
app.py - FastAPI server for Healthcare Environment
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from fastapi import Request
from fastapi.responses import JSONResponse, HTMLResponse
from openenv.core.env_server import create_fastapi_app
from models import HealthAction, HealthObservation
from server.environment import HealthCareEnvironment, TASKS

app = create_fastapi_app(HealthCareEnvironment, HealthAction, HealthObservation)

_UI_HTML = """
<!DOCTYPE html>
<html>
<head><title>Healthcare Environment</title></head>
<body>
    <h1>Healthcare Environment Analytics Server</h1>
    <p>This is a headless OpenEnv server. Visit <a href="/docs">/docs</a> for the API.</p>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def root():
    """Serve the interactive UI."""
    return HTMLResponse(content=_UI_HTML)

@app.get("/info")
def info():
    return JSONResponse(content={
        "name": "Healthcare SQL Environment",
        "version": "1.0.0",
        "status": "running",
        "total_tasks": len(TASKS),
        "difficulty_breakdown": {
            "easy": len([t for t in TASKS.values() if t["difficulty"] == "easy"]),
            "medium": len([t for t in TASKS.values() if t["difficulty"] == "medium"]),
            "hard": len([t for t in TASKS.values() if t["difficulty"] == "hard"]),
        },
        "endpoints": {
            "ui": "/",
            "health": "/health",
            "docs": "/docs",
            "tasks": "/tasks",
            "grader": "/grader",
            "baseline": "/baseline",
            "reset": "/reset",
            "step": "/step",
            "state": "/state",
        }
    })

@app.get("/tasks", tags=["Competition"])
def get_tasks():
    return JSONResponse(content={
        "tasks": HealthCareEnvironment.list_tasks(),
        "total": len(TASKS),
        "action_schema": {
            "sql_query": "string - The fixed SQL query to submit",
            "explanation": "string (optional) - Agent reasoning",
        },
    })

@app.post("/grader", tags=["Competition"])
def run_grader(task_id: str, sql_query: str):
    result = HealthCareEnvironment.run_grader(task_id, sql_query)
    return JSONResponse(content=result)

@app.get("/baseline", tags=["Competition"])
def run_baseline():
    baseline_scores = {}
    for task_id, task in TASKS.items():
        result = HealthCareEnvironment.run_grader(task_id, task["expected_query"])
        baseline_scores[task_id] = {
            "score": result["score"],
            "passed": result["passed"],
            "difficulty": task["difficulty"],
            "feedback": result["feedback"],
        }
    avg = sum(v["score"] for v in baseline_scores.values()) / len(baseline_scores) if baseline_scores else 0
    return JSONResponse(content={
        "baseline_agent": "oracle",
        "results": baseline_scores,
        "average_score": round(avg, 4),
    })

def main():
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    host = os.environ.get("HOST", "0.0.0.0")
    workers = int(os.environ.get("WORKERS", 4))
    uvicorn.run("app:app", host=host, port=port, workers=workers)

if __name__ == "__main__":
    main()
