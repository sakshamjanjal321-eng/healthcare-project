#!/usr/bin/env python3
"""
inference.py - HealthCare Environment Baseline Agent
"""

import os
from typing import Any, Dict, List, Optional
import requests
from openai import OpenAI

API_KEY = os.environ.get("API_KEY")
API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_URL = os.environ.get("ENV_URL", "http://0.0.0.0:7860")

ALL_TASKS = [
    ("task_1", "easy"),
    ("task_2", "easy"),
    ("task_3", "medium"),
    ("task_4", "hard"),
]

SYSTEM_PROMPT = """You are an expert SQL developer. Fix broken SQL queries.
Return ONLY the corrected SQL query — no markdown, no explanation."""

def build_prompt(obs: Dict[str, Any]) -> str:
    parts = [
        f"Task: {obs.get('task_description', '')}",
        "",
        "Database Schema:",
        obs.get("db_schema", ""),
        "",
        "Broken Query:",
        obs.get("broken_query", ""),
    ]
    if obs.get("expected_columns"):
        parts += ["", f"Expected output columns: {obs['expected_columns']}"]
    parts += ["", "Return ONLY the corrected SQL query:"]
    return "\n".join(parts)

def extract_sql(text: str) -> str:
    text = text.strip()
    if "```" in text:
        blocks = text.split("```")
        if len(blocks) >= 2:
            code = blocks[1].strip()
            if code.lower().startswith("sql"): return code[3:].strip()
            return code
    if text.startswith('"') and text.endswith('"'): return text[1:-1]
    return text

class EnvClient:
    def __init__(self, base_url: str):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()

    def health(self) -> Dict[str, Any]:
        return self.session.get(f"{self.base}/health").json()

    def reset(self, task_id: str) -> Dict[str, Any]:
        return self.session.post(f"{self.base}/reset", json={"task_id": task_id}).json()

    def step(self, sql_query: str) -> Dict[str, Any]:
        return self.session.post(f"{self.base}/step", json={"action": {"sql_query": sql_query}}).json()

def run_task(task_id: str, env: EnvClient, client: OpenAI):
    try:
        resp = env.reset(task_id)
        obs = resp.get("observation", {})
        done = resp.get("done", False)

        for step in range(1, 6):
            if done: break
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": build_prompt(obs)}],
                max_tokens=200, temperature=0.0
            )
            sql = extract_sql(completion.choices[0].message.content or "")
            resp = env.step(sql)
            obs = resp.get("observation", {})
            done = resp.get("done", False)
            print(f"[STEP] {step} | Task {task_id} | Score: {resp.get('reward', 0)}")
    except Exception as e:
        print(f"Error on {task_id}: {e}")

def main():
    if not API_KEY:
        print("API_KEY not set. Exiting.")
        return
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = EnvClient(ENV_URL)
    for task_id, _ in ALL_TASKS:
        print(f"--- Running {task_id} ---")
        run_task(task_id, env, client)

if __name__ == "__main__":
    main()
