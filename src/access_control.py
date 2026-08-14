
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import pandas as pd


ROLE_ACTIONS = {
    "viewer": {"read_summary", "read_metrics"},
    "analyst": {"read_summary", "read_metrics", "read_redacted", "read_audit"},
    "auditor": {"read_metrics", "read_audit"},
    "pipeline": {"read_silver", "write_detections", "write_gold", "write_docx"},
    "admin": {"*"},
}


class AccessController:
    """Lightweight RBAC simulation with an append-only in-memory audit list."""

    def __init__(self):
        self.records: List[Dict] = []

    def record_access(
        self,
        user: str,
        role: str,
        action: str,
        dataset: str,
    ) -> Dict:
        allowed_actions = ROLE_ACTIONS.get(role, set())
        access_granted = "*" in allowed_actions or action in allowed_actions

        record = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "user": user,
            "role": role,
            "dataset": dataset,
            "action": action,
            "access_granted": access_granted,
        }
        self.records.append(record)
        return record

    def write_csv(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(self.records).to_csv(path, index=False, encoding="utf-8")