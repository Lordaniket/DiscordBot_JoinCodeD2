from pymongo import MongoClient
import json

print("This is changes in database")
# Load configuration from JSON file
with open("config.json", "r") as file:
    config = json.load(file)

MONGO_URI = config.get("MONGO_URI")

# MongoDB Setup
client = MongoClient(MONGO_URI)
db = client["discord_bot"]
collection = db["join_codes"]

def save_join_code(user_id, join_code):
    """Save or update a user's join code in MongoDB"""
    collection.update_one(
        {"user_id": user_id},
        {"$set": {"code": join_code}},
        upsert=True
    )

def get_join_code(user_id):
    """Retrieve a user's join code"""
    result = collection.find_one({"user_id": user_id})
    return result["code"] if result else None

def delete_join_code(user_id):
    """Delete a user's join code"""
    collection.delete_one({"user_id": user_id})

def clear_all_codes():
    """Delete all join codes (admin only)"""
    collection.delete_many({})
