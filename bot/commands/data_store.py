import json
import os

DATA_DIR = "data"

LINKS_FILE = os.path.join(DATA_DIR, "ijudge_links.json")
SCHEDULES_FILE = os.path.join(DATA_DIR, "feedback_links.json")
SETUP_FILE = os.path.join(DATA_DIR, "setup.json")

os.makedirs(DATA_DIR, exist_ok=True)


def load_json(file_path: str, default=None) -> list:
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path: str, data: list) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_links() -> list:
    return load_json(LINKS_FILE)


def save_links(data: list) -> None:
    save_json(LINKS_FILE, data)


def load_schedules() -> list:
    return load_json(SCHEDULES_FILE)


def save_schedules(data: list) -> None:
    save_json(SCHEDULES_FILE, data)

def load_setup() -> int | None:
    return load_json(SETUP_FILE, default=None)


def save_setup(channel_id: int) -> None:
    save_json(SETUP_FILE, channel_id)