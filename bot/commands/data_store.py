"""data_store for feedback and ijudge cmd"""
import json
import os

# ===== Constants =====
# Directory to store JSON files
DATA_DIR = "data"

# File paths for iJudge and Feedback links
LINKS_FILE = os.path.join(DATA_DIR, "ijudge_links.json")
SCHEDULES_FILE = os.path.join(DATA_DIR, "feedback_links.json")

# Ensure the 'data' folder exists
os.makedirs(DATA_DIR, exist_ok=True)


# ===== Utility Functions =====
def load_json(file_path: str) -> list:
    """
    Load JSON data from the specified file.
    Returns an empty list if the file does not exist.
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path: str, data: list) -> None:
    """
    Save data to the specified JSON file in a readable (indented) format.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ===== Specific File Accessors =====
def load_links() -> list:
    """Load all iJudge links from the ijudge_links.json file."""
    return load_json(LINKS_FILE)


def save_links(data: list) -> None:
    """Save iJudge links to the ijudge_links.json file."""
    save_json(LINKS_FILE, data)


def load_schedules() -> list:
    """Load all feedback schedule links from the feedback_links.json file."""
    return load_json(SCHEDULES_FILE)


def save_schedules(data: list) -> None:
    """Save feedback schedule links to the feedback_links.json file."""
    save_json(SCHEDULES_FILE, data)
