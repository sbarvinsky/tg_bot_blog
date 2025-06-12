import json
import os
from datetime import datetime

DATA_DIR = "data"
IDEAS_FILE = os.path.join(DATA_DIR, "ideas.json")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")

os.makedirs(DATA_DIR, exist_ok=True)

def init_db(file, default=dict):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump(default(), f, indent=2, ensure_ascii=False)

def save_idea(idea_text, user_id, category=None):
    init_db(IDEAS_FILE, lambda: {})
    with open(IDEAS_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        user_key = str(user_id)
        if user_key not in data:
            data[user_key] = []
        data[user_key].append({
            "text": idea_text,
            "category": category,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "new"
        })
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()

def get_ideas(user_id):
    init_db(IDEAS_FILE, lambda: {})
    with open(IDEAS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get(str(user_id), [])

def get_categories(user_id):
    init_db(CATEGORIES_FILE, lambda: {})
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get(str(user_id), [])

def add_category(user_id, category):
    init_db(CATEGORIES_FILE, lambda: {})
    with open(CATEGORIES_FILE, 'r+', encoding='utf-8') as f:
        data = json.load(f)
        user_key = str(user_id)
        if user_key not in data:
            data[user_key] = []
        if category not in data[user_key]:
            data[user_key].append(category)
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()
