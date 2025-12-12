from pymongo import MongoClient

def get_database():
    # client = MongoClient("mongodb://localhost:27017/")
    client = MongoClient("mongodb+srv://gautammahendra464_db_user:eJHf5YAugjm8yNu4@mahendra464.s7mwp9j.mongodb.net/?appName=mahendra464")
    db = client["restro_project"]
    return db

def create_user(user_data):
    db = get_database()
    collection = db['users']
    result = collection.insert_one(user_data)
    return result.inserted_id

def get_reviews_collection():
    db = get_database()
    return db["reviews"]

