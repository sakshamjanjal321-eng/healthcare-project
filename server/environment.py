import sqlite3
import uuid
import random
import os
import sys
import hashlib
from typing import Optional, Dict, List, Tuple, Any, Set

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from openenv.core.env_server import Environment
from models import HealthAction, HealthObservation, HealthState

# ── Database Schema ───────────────────────────────────────────────────────────

DB_SCHEMA = """
CREATE TABLE visitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT,
    user_agent TEXT,
    path TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT,
    booking_date TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

DB_SEED = """
INSERT INTO visitors (ip_address, user_agent, path, timestamp) VALUES ('192.168.1.1', 'Mozilla', '/index', '2026-04-10 10:00:00');
INSERT INTO visitors (ip_address, user_agent, path, timestamp) VALUES ('192.168.1.2', 'Chrome', '/about', '2026-04-10 10:05:00');
INSERT INTO visitors (ip_address, user_agent, path, timestamp) VALUES ('192.168.1.3', 'Safari', '/fitness', '2026-04-10 10:10:00');
INSERT INTO visitors (ip_address, user_agent, path, timestamp) VALUES ('192.168.1.4', 'Firefox', '/diet', '2026-04-11 11:00:00');
INSERT INTO visitors (ip_address, user_agent, path, timestamp) VALUES ('192.168.1.1', 'Mozilla', '/fitness', '2026-04-11 11:05:00');
INSERT INTO visitors (ip_address, user_agent, path, timestamp) VALUES ('192.168.1.5', 'Chrome', '/index', '2026-04-11 11:10:00');

INSERT INTO bookings (full_name, email, booking_date, timestamp) VALUES ('Alice Smith', 'alice@test.com', '2026-04-12', '2026-04-10 12:00:00');
INSERT INTO bookings (full_name, email, booking_date, timestamp) VALUES ('Bob Jones', 'bob@test.com', '2026-04-12', '2026-04-10 13:00:00');
INSERT INTO bookings (full_name, email, booking_date, timestamp) VALUES ('Charlie Brown', 'charlie@test.com', '2026-04-13', '2026-04-11 14:00:00');
"""

SCHEMA_DESCRIPTION = """Tables available:

visitors(id, ip_address, user_agent, path, timestamp)
bookings(id, full_name, email, booking_date, timestamp)
"""

TASKS: Dict[str, Dict[str, Any]] = {
    "task_1": {
        "id": "task_1", "difficulty": "easy",
        "description": "Count the total number of bookings in the database.",
        "broken_query": "SELECT CONT(*) AS total_bookings FORM bookings",
        "expected_query": "SELECT COUNT(*) AS total_bookings FROM bookings",
        "hint": "Fix typos: CONT -> COUNT, FORM -> FROM",
    },
    "task_2": {
        "id": "task_2", "difficulty": "easy",
        "description": "Get all distinct IP addresses of visitors.",
        "broken_query": "SELECT DESTINCT ip_address FROM visitors",
        "expected_query": "SELECT DISTINCT ip_address FROM visitors",
        "hint": "DESTINCT -> DISTINCT",
    },
    "task_3": {
        "id": "task_3", "difficulty": "medium",
        "description": "Get the full names of all bookings made on '2026-04-12'.",
        "broken_query": "SELECT full_name FROM bookings WHER booking_date = '2026-04-12'",
        "expected_query": "SELECT full_name FROM bookings WHERE booking_date = '2026-04-12'",
        "hint": "WHER -> WHERE",
    },
    "task_4": {
        "id": "task_4", "difficulty": "hard",
        "description": "Find the paths visited by more than 1 visitor.",
        "broken_query": "SELECT path, COUNT(*) AS visitor_count FROM visitors WHERE COUNT(*) > 1 GROUP BY path",
        "expected_query": "SELECT path, COUNT(*) AS visitor_count FROM visitors GROUP BY path HAVING COUNT(*) > 1",
        "hint": "Cannot use aggregate functions in WHERE. Use HAVING after GROUP BY.",
    },
}

def create_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(DB_SCHEMA + DB_SEED)
    return conn

def run_query(conn, query: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
    try:
        cursor = conn.execute(query)
        rows   = [dict(row) for row in cursor.fetchall()]
        return rows, None
    except Exception as exc:
        return None, str(exc)

def _normalize_rows(rows: List[Dict]) -> List[tuple]:
    def norm(v: Any) -> str:
        if isinstance(v, float): return str(round(v, 2))
        return str(v)
    return sorted([tuple(sorted((k, norm(v)) for k, v in row.items())) for row in rows])

def _hash_query(query: str) -> str:
    return hashlib.md5(query.strip().lower().encode()).hexdigest()

def grade_submission(
    task_id: str, submitted_rows: Optional[List[Dict]], error: Optional[str], conn,
    submitted_hash: str, previous_hashes: Set[str], broken_hash: str,
) -> Tuple[float, str]:
    task = TASKS[task_id]
    score = 0.0
    feedback = []

    if submitted_hash == broken_hash:
        return 0.001, "Submitted the original broken query unchanged."

    if submitted_hash in previous_hashes:
        return 0.001, "Exact query already submitted."

    if error is not None:
        return 0.001, f"Query failed: {error}"

    expected_rows, _ = run_query(conn, task["expected_query"])

    score += 0.30
    feedback.append("Executes without error (+0.30)")

    sub_cols = set(submitted_rows[0].keys()) if submitted_rows else set()
    exp_cols = set(expected_rows[0].keys())  if expected_rows  else set()
    if sub_cols == exp_cols:
        score += 0.20
        feedback.append("Correct columns (+0.20)")
    else:
        feedback.append("Wrong columns.")

    sub_count = len(submitted_rows) if submitted_rows else 0
    exp_count = len(expected_rows)  if expected_rows  else 0
    if sub_count == exp_count:
        score += 0.10
        feedback.append(f"Correct row count (+0.10)")
    else:
        feedback.append(f"Wrong row count: got {sub_count}, expected {exp_count}")

    if submitted_rows and expected_rows:
        sub_norm = _normalize_rows(submitted_rows)
        exp_norm = _normalize_rows(expected_rows)
        if sub_norm == exp_norm:
            score += 0.40
            feedback.append("All row values match exactly! (+0.40)")
        elif sub_count == exp_count and sub_count > 0:
            matching = sum(1 for s, e in zip(sub_norm, exp_norm) if s == e)
            partial  = (matching / exp_count) * 0.40
            score   += partial
            feedback.append(f"Partial match (+{partial:.2f})")
        else:
            feedback.append("Row values do not match.")

    score = max(0.001, min(0.999, round(score, 4)))
    return score, " | ".join(feedback)


class HealthCareEnvironment(Environment):
    SUPPORTS_CONCURRENT_SESSIONS = True
    MAX_ATTEMPTS = 5

    def __init__(self):
        self._state = HealthState()
        self._task = None
        self._conn = None
        self._attempt = 0
        self._last_score = 0.001
        self._previous_hashes: Set[str] = set()
        self._broken_hash = ""

    def reset(self, seed=None, episode_id=None, task_id=None, **kwargs) -> HealthObservation:
        if task_id and task_id in TASKS:
            self._task = TASKS[task_id]
        else:
            self._task = random.choice(list(TASKS.values()))

        if self._conn:
            self._conn.close()
        self._conn = create_db()
        self._attempt = 0
        self._last_score = 0.001
        self._previous_hashes = set()
        self._broken_hash = _hash_query(self._task["broken_query"])

        exp_rows, _ = run_query(self._conn, self._task["expected_query"])
        exp_cols = list(exp_rows[0].keys()) if exp_rows else []
        exp_count = len(exp_rows) if exp_rows else -1

        self._state = HealthState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_id=self._task["id"],
            difficulty=self._task["difficulty"],
            max_attempts=self.MAX_ATTEMPTS,
            last_score=0.001,
            completed=False,
            attempts_used=0,
        )

        return HealthObservation(
            done=False, reward=0.001, broken_query=self._task["broken_query"],
            db_schema=SCHEMA_DESCRIPTION, error_message="", task_description=self._task["description"],
            task_id=self._task["id"], difficulty=self._task["difficulty"], attempt_number=0,
            max_attempts=self.MAX_ATTEMPTS, feedback="Episode started.", hint="",
            expected_columns=exp_cols, expected_row_count=exp_count,
        )

    def step(self, action: HealthAction, timeout_s=None, **kwargs) -> HealthObservation:
        self._attempt += 1
        self._state.step_count += 1
        self._state.attempts_used = self._attempt

        submitted_hash = _hash_query(action.sql_query)
        rows, error = run_query(self._conn, action.sql_query)

        score, feedback = grade_submission(
            self._task["id"], rows, error, self._conn, submitted_hash, self._previous_hashes, self._broken_hash,
        )

        self._previous_hashes.add(submitted_hash)
        self._last_score = score
        self._state.last_score = score

        done = (score >= 0.99) or (self._attempt >= self.MAX_ATTEMPTS)
        self._state.completed = score >= 0.99

        reward = max(0.001, min(0.999, score))
        if done and score < 0.99 and self._attempt >= self.MAX_ATTEMPTS:
            reward = max(0.001, round(score * 0.85, 4))

        hint = ""
        if self._attempt >= 2 and score < 0.5:
            hint = self._task["hint"]

        exp_rows, _ = run_query(self._conn, self._task["expected_query"])
        exp_cols = list(exp_rows[0].keys()) if exp_rows else []
        exp_count = len(exp_rows) if exp_rows else -1

        return HealthObservation(
            done=done, reward=reward, broken_query=self._task["broken_query"],
            db_schema=SCHEMA_DESCRIPTION, error_message=error or "", task_description=self._task["description"],
            task_id=self._task["id"], difficulty=self._task["difficulty"], attempt_number=self._attempt,
            max_attempts=self.MAX_ATTEMPTS, feedback=feedback, hint=hint,
            expected_columns=exp_cols, expected_row_count=exp_count,
        )

    @property
    def state(self) -> HealthState:
        return self._state

    @staticmethod
    def list_tasks() -> List[Dict]:
        return [
            {
                "task_id": t["id"],
                "difficulty": t["difficulty"],
                "description": t["description"],
                "broken_query": t["broken_query"],
                "action_schema": {
                    "sql_query": "string (required) - Your corrected SQL query",
                    "explanation": "string (optional) - Your reasoning",
                },
            }
            for t in TASKS.values()
        ]

    @staticmethod
    def run_grader(task_id: str, sql_query: str) -> Dict:
        if task_id not in TASKS:
            return {"error": f"Unknown task_id '{task_id}'"}
        conn = create_db()
        submitted_hash = _hash_query(sql_query)
        broken_hash = _hash_query(TASKS[task_id]["broken_query"])
        rows, error = run_query(conn, sql_query)
        score, feedback = grade_submission(task_id, rows, error, conn, submitted_hash, set(), broken_hash)
        conn.close()
        return {"task_id": task_id, "score": score, "feedback": feedback, "passed": score >= 0.99}
