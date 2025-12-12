from pymongo import MongoClient

# client = MongoClient("mongodb://localhost:27017/")

client = MongoClient("mongodb+srv://gautammahendra464_db_user:eJHf5YAugjm8yNu4@mahendra464.s7mwp9j.mongodb.net/?appName=mahendra46")

db = client["ecommerce"]

collection = db["products"]

data = collection.find()

for document in data:
    print(document)