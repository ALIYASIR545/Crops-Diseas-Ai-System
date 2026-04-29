import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                farmer_id TEXT NOT NULL,
                crop TEXT,
                image_path TEXT NOT NULL,
                disease_key TEXT NOT NULL,
                confidence REAL NOT NULL,
                weather_risk TEXT DEFAULT 'unknown',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def insert_prediction(
    db_path: Path,
    farmer_id: str,
    crop: str,
    image_path: str,
    disease_key: str,
    confidence: float,
    weather_risk: str,
) -> int:
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO predictions (farmer_id, crop, image_path, disease_key, confidence, weather_risk)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (farmer_id, crop, image_path, disease_key, confidence, weather_risk),
        )
        conn.commit()
        return int(cur.lastrowid)


def fetch_history(db_path: Path, farmer_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        if farmer_id:
            rows = conn.execute(
                """
                SELECT id, farmer_id, crop, disease_key, confidence, weather_risk, created_at
                FROM predictions
                WHERE farmer_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (farmer_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, farmer_id, crop, disease_key, confidence, weather_risk, created_at
                FROM predictions
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    return [dict(row) for row in rows]


def delete_history_item(db_path: Path, history_id: int, farmer_id: Optional[str] = None) -> int:
    with sqlite3.connect(db_path) as conn:
        if farmer_id:
            cur = conn.execute(
                """
                DELETE FROM predictions
                WHERE id = ? AND farmer_id = ?
                """,
                (history_id, farmer_id),
            )
        else:
            cur = conn.execute(
                """
                DELETE FROM predictions
                WHERE id = ?
                """,
                (history_id,),
            )
        conn.commit()
        return int(cur.rowcount)
