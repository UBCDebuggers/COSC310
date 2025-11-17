from pathlib import Path
import csv
import os
import logging
from typing import List, Dict, Any
from datetime import datetime
from abc import ABC

logger = logging.getLogger(__name__)

# Abstract base repository -> Eliminates code duplication across modules and CSV handling
class BaseCSVRepository(ABC):
    DATA_PATH: Path
    FIELDNAMES: List[str]
    DATETIME_FIELDS: List[str] = []  

    @classmethod
    def load_all(cls) -> List[Dict[str, Any]]:
        if not cls.DATA_PATH.exists():
            return []
        
        items = []
        try:
            with cls.DATA_PATH.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f, delimiter=';')
                for row in reader:
                    cls._parse_datetime_fields(row)
                    items.append(row)
        except Exception as e:
            logger.error(f"Error reading CSV {cls.DATA_PATH}: {e}")
        return items

    @classmethod
    def save_all(cls, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            cls.DATA_PATH.unlink(missing_ok=True)
            return
        
        try:
            serializable = []
            for row in rows:
                serialized_row = {
                    k: (v.isoformat() if isinstance(v, datetime) else v)
                    for k, v in row.items()
                }
                serializable.append(serialized_row)
            
            tmp = cls.DATA_PATH.with_suffix('.tmp')
            with tmp.open('w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=cls.FIELDNAMES, delimiter=';')
                writer.writeheader()
                writer.writerows(serializable)
            os.replace(tmp, cls.DATA_PATH)
        except Exception as e:
            logger.error(f"Error writing CSV {cls.DATA_PATH}: {e}")
            raise

    @classmethod
    def _parse_datetime_fields(cls, row: Dict[str, Any]) -> None:
        for field in cls.DATETIME_FIELDS:
            if field in row and row[field]:
                try:
                    row[field] = datetime.fromisoformat(row[field])
                except Exception as e:
                    logger.warning(f"Failed to parse {field}={row[field]}: {e}")