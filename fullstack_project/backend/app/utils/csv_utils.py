import csv
import os

def read_csv(path):
    """
    Safely read CSV file and return list of dictionaries.
    Returns [] if file does not exist.
    """
    if not path.exists():
        return []
    
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def write_csv(path, rows):
    """
    Safely write list of dictionaries to CSV.
    Uses a temp file + atomic replace for safety.
    """
    if not rows:
        path.unlink(missing_ok=True)
        return
    
    fieldnames = list(rows[0].keys())
    tmp = path.with_suffix(".tmp")

    with tmp.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    os.replace(tmp, path)
