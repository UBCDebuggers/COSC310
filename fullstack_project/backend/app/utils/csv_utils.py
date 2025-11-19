import csv
import os

# Shared CSV reader with optional delimiter and encoding.
# Added parameters so books_repo can use ';' + latin-1.
def read_csv(path, delimiter=",", encoding="utf-8"):
    if not path.exists():
        return []   # If file doesn't exist, mimic repo behavior.
    
    with path.open("r", encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        return [row for row in reader]


# Shared CSV writer with same flexibility.
# Still uses temp-file + atomic replace, same as the repos originally did.
def write_csv(path, rows, delimiter=",", encoding="utf-8"):
    if not rows:
        path.unlink(missing_ok=True)
        return
    
    fieldnames = list(rows[0].keys())
    tmp = path.with_suffix(".tmp")

    with tmp.open("w", encoding=encoding, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)

    os.replace(tmp, path)
