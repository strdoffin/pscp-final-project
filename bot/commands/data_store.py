import json
import os

LINKS_FILE = "data/ijudge_links.json"
SCHEDULES_FILE = "data/feedback_links.json"

os.makedirs("data", exist_ok=True)

def load_links():
    if not os.path.exists(LINKS_FILE):
        return []
    with open(LINKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_links(data):
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_schedules():
    if not os.path.exists(SCHEDULES_FILE):
        return []
    with open(SCHEDULES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_schedules(data):
    with open(SCHEDULES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
