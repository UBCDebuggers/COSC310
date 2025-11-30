from pathlib import Path
import csv, os, uuid
from typing import List, Dict, Any
from datetime import datetime
import logging
import dateutil

logger = logging.getLogger(__name__)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "notification.csv"

def load_all() -> List[Dict[str, Any]]:
    if not DATA_PATH.exists():
        return []

    items: List[Dict[str, Any]] = []
    with DATA_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if 'timestamp' in row and row['timestamp']:
                orig_ts = row['timestamp']
                try:
                    if dateutil:
                        row['timestamp'] = dateutil.parser.isoparse(orig_ts)
                    else:
                        ts = orig_ts
                        if isinstance(ts, str) and ts.endswith('Z'):
                            ts = ts.replace('Z', '+00:00')
                        row['timestamp'] = datetime.fromisoformat(ts)
                except Exception as e:
                    logger.warning("Failed to parse timestamp %r: %s", orig_ts, e)
            items.append(row)
    return items

def save_all(notifications: List[Dict[str, Any]]) -> None:
    if not notifications:
        DATA_PATH.unlink(missing_ok=True)
        return

    serializable = []
    for row in notifications:
        r = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in row.items()}
        serializable.append(r)

    fieldnames = list(notifications[0].keys())
    tmp = DATA_PATH.with_suffix(".tmp")

    with tmp.open("w", encoding="latin-1", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(serializable)

    os.replace(tmp, DATA_PATH)

