from __future__ import annotations

import json
import sqlite3
from io import StringIO
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd


class SQLiteAnalysisStore:
    def __init__(self, db_path: str | Path = "backend/data/risk_analysis.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def ping(self) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("SELECT 1").fetchone()
            return True
        except sqlite3.Error:
            return False

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    frame_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS analyses (
                    analysis_id TEXT PRIMARY KEY,
                    dataset_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary_json TEXT NOT NULL,
                    pca_json TEXT NOT NULL,
                    risk_json TEXT NOT NULL,
                    metrics_json TEXT NOT NULL,
                    scenarios_json TEXT NOT NULL,
                    report_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS scenario_runs (
                    scenario_id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    scenarios_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    analysis_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    report_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save_dataset(self, frame: pd.DataFrame) -> str:
        dataset_id = str(uuid4())
        frame_json = frame.to_json(orient="split")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO datasets (dataset_id, frame_json) VALUES (?, ?)",
                (dataset_id, frame_json),
            )
            conn.commit()
        return dataset_id

    def get_dataset(self, dataset_id: str) -> pd.DataFrame:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT frame_json FROM datasets WHERE dataset_id = ?",
                (dataset_id,),
            ).fetchone()
        if row is None:
            raise KeyError("dataset not found")
        return pd.read_json(StringIO(row[0]), orient="split")

    def save_analysis(
        self,
        dataset_id: str,
        summary: dict[str, Any],
        pca: dict[str, Any],
        risk: dict[str, Any],
        metrics: dict[str, Any],
    ) -> str:
        analysis_id = str(uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO analyses (
                    analysis_id, dataset_id, status, summary_json, pca_json,
                    risk_json, metrics_json, scenarios_json, report_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    analysis_id,
                    dataset_id,
                    "completed",
                    json.dumps(summary),
                    json.dumps(pca),
                    json.dumps(risk),
                    json.dumps(metrics),
                    json.dumps({}),
                    json.dumps({}),
                ),
            )
            conn.commit()
        return analysis_id

    def get_analysis(self, analysis_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT analysis_id, dataset_id, status, summary_json, pca_json,
                       risk_json, metrics_json, scenarios_json, report_json
                FROM analyses
                WHERE analysis_id = ?
                """,
                (analysis_id,),
            ).fetchone()
        if row is None:
            raise KeyError("analysis not found")
        return {
            "analysis_id": row[0],
            "dataset_id": row[1],
            "status": row[2],
            "summary": json.loads(row[3]),
            "pca": json.loads(row[4]),
            "risk": json.loads(row[5]),
            "metrics": json.loads(row[6]),
            "scenarios": json.loads(row[7]),
            "report": json.loads(row[8]),
        }

    def save_scenario_run(self, analysis_id: str, scenarios: dict[str, Any]) -> str:
        _ = self.get_analysis(analysis_id)
        scenario_id = str(uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO scenario_runs (scenario_id, analysis_id, status, scenarios_json)
                VALUES (?, ?, ?, ?)
                """,
                (scenario_id, analysis_id, "completed", json.dumps(scenarios)),
            )
            conn.execute(
                "UPDATE analyses SET scenarios_json = ? WHERE analysis_id = ?",
                (json.dumps(scenarios), analysis_id),
            )
            conn.commit()
        return scenario_id

    def get_scenario_run(self, scenario_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT scenario_id, analysis_id, status, scenarios_json
                FROM scenario_runs
                WHERE scenario_id = ?
                """,
                (scenario_id,),
            ).fetchone()
        if row is None:
            raise KeyError("scenario not found")
        return {
            "scenario_id": row[0],
            "analysis_id": row[1],
            "status": row[2],
            "scenarios": json.loads(row[3]),
        }

    def save_report(self, analysis_id: str, report: dict[str, Any]) -> str:
        _ = self.get_analysis(analysis_id)
        report_id = str(uuid4())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO reports (report_id, analysis_id, status, report_json)
                VALUES (?, ?, ?, ?)
                """,
                (report_id, analysis_id, "completed", json.dumps(report)),
            )
            conn.execute(
                "UPDATE analyses SET report_json = ? WHERE analysis_id = ?",
                (json.dumps(report), analysis_id),
            )
            conn.commit()
        return report_id

    def get_report(self, report_id: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT report_id, analysis_id, status, report_json
                FROM reports
                WHERE report_id = ?
                """,
                (report_id,),
            ).fetchone()
        if row is None:
            raise KeyError("report not found")
        return {
            "report_id": row[0],
            "analysis_id": row[1],
            "status": row[2],
            "report": json.loads(row[3]),
        }


store = SQLiteAnalysisStore()
