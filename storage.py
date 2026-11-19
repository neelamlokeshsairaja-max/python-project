"""Atomic JSON-in-TXT persistence helpers."""
import json
import os
from pathlib import Path
from exceptions import StorageError

def save_snapshot(path, payload):
    path = Path(path)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with temporary_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except (OSError, TypeError, ValueError) as exc:
        try:
            if temporary_path.exists():
                temporary_path.unlink()
        except OSError:
            pass
        raise StorageError(f"Could not save bank data: {exc}") from exc

def load_snapshot(path):
    path = Path(path)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("The data file must contain a JSON object.")
        return data
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        # Never silently replace damaged data with an empty bank.
        raise StorageError(f"Could not load bank data from {path}: {exc}") from exc
