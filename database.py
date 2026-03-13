from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import date, datetime
import hashlib
import os

MONGO_URI = st.secrets.get("MONGO_URI") or os.getenv("MONGO_URI")
mongo = MongoClient(MONGO_URI)
db = mongo["mathapp"]
users = db["users"]
progress = db["user_progress"]
assignments = db["assignments"]

def _hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, ip="Unknown", user_agent="Unknown"):
    if users.find_one({"username": username}):
        return False, "Username already exists"
    users.insert_one({
        "username": username,
        "password": _hash_password(password),
        "registered_at": datetime.utcnow().isoformat(),
        "registered_ip": ip,
        "registered_device": user_agent,
    })
    return True, "Account created"

def login_user(username, password):
    return users.find_one({"username": username,
                           "password": _hash_password(password)}) is not None

def get_progress(username):
    return progress.find_one({"username": username})

def create_progress(username, grade, level):
    today = str(date.today())
    progress.insert_one({
        "username": username,
        "grade": grade,
        "level": level,
        "streak": 0,
        "total_answered": 0,
        "total_correct": 0,
        "daily_date": today,
        "daily_answered": 0,
        "daily_correct": 0,
        "badges": [],
    })

def update_progress(username, correct, total):
    today = str(date.today())
    p = get_progress(username)
    if p.get("daily_date") != today:
        progress.update_one(
            {"username": username},
            {"$set": {"daily_date": today,
                      "daily_answered": total,
                      "daily_correct": correct},
             "$inc": {"total_answered": total, "total_correct": correct}}
        )
    else:
        progress.update_one(
            {"username": username},
            {"$inc": {
                "total_answered": total, "total_correct": correct,
                "daily_answered": total, "daily_correct": correct,
            }}
        )

def award_badges(username, new_badges):
    if new_badges:
        progress.update_one(
            {"username": username},
            {"$addToSet": {"badges": {"$each": new_badges}}}
        )

def get_assignments(username):
    return list(assignments.find({"username": username}))

def create_assignments(username, level, topics):
    for topic in topics:
        assignments.insert_one({
            "username": username,
            "level": level,
            "topic": topic,
            "quiz_1_done": False, "quiz_1_score": 0,
            "quiz_2_done": False, "quiz_2_score": 0,
        })

def complete_quiz(username, topic, quiz_num, score):
    field = f"quiz_{quiz_num}"
    assignments.update_one(
        {"username": username, "topic": topic},
        {"$set": {f"{field}_done": True, f"{field}_score": score}}
    )

def all_assignments_complete(username, level):
    return assignments.find_one({
        "username": username, "level": level,
        "$or": [{"quiz_1_done": False}, {"quiz_2_done": False}]
    }) is None

def advance_level(username):
    p = get_progress(username)
    new_level = p["level"] + 1
    progress.update_one({"username": username}, {"$set": {"level": new_level}})
    return new_level

def delete_assignments(username, level):

    assignments.delete_many({"username": username, "level": level})
