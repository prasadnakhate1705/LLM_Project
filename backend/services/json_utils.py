import json
from datetime import datetime, timedelta

SESSIONS_FILE = "gesture_sessions.json"

def load_sessions():
    try:
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_sessions(sessions):
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

def remove_old_sessions(sessions, years=5):
    cutoff = datetime.now() - timedelta(days=365 * years)
    return [s for s in sessions if datetime.fromisoformat(s["timestamp"]) > cutoff]
