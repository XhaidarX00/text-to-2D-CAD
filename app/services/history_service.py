"""History Service — JSON-based storage for CAD generation history."""
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Optional


HISTORY_FILE = "history.json"


def _read_history() -> list[dict]:
    """Read all history entries from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def _write_history(entries: list[dict]):
    """Write history entries to JSON file."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False, default=str)


def create_entry(
    prompt: str,
    params: dict,
    dxf_filename: str,
    svg_preview: str = "",
) -> dict:
    """Create a new history entry and persist to file."""
    entry = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "params": params,
        "dxf_filename": dxf_filename,
        "stl_filename": None,
        "svg_preview": svg_preview,
    }

    entries = _read_history()
    entries.insert(0, entry)  # newest first
    _write_history(entries)
    return entry


def get_all_entries() -> list[dict]:
    """Return all history entries (newest first)."""
    return _read_history()


def get_entry(entry_id: str) -> Optional[dict]:
    """Get a single history entry by ID."""
    entries = _read_history()
    for entry in entries:
        if entry.get("id") == entry_id:
            return entry
    return None


def update_entry(entry_id: str, updates: dict) -> Optional[dict]:
    """
    Update fields of a history entry.
    Allowed fields: prompt, params, stl_filename.
    """
    entries = _read_history()
    for i, entry in enumerate(entries):
        if entry.get("id") == entry_id:
            allowed = {"prompt", "params", "stl_filename"}
            for key, value in updates.items():
                if key in allowed:
                    entries[i][key] = value
            entries[i]["updated_at"] = datetime.now(timezone.utc).isoformat()
            _write_history(entries)
            return entries[i]
    return None


def delete_entry(entry_id: str) -> bool:
    """Delete a history entry by ID. Returns True if found and deleted."""
    entries = _read_history()
    original_len = len(entries)
    entries = [e for e in entries if e.get("id") != entry_id]

    if len(entries) < original_len:
        _write_history(entries)
        return True
    return False


def clear_all() -> int:
    """Delete all history entries. Returns count of deleted entries."""
    entries = _read_history()
    count = len(entries)
    _write_history([])
    return count
