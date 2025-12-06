from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")  

db = client["ecommerce"]

collection = db["products"]

data = collection.find()

for document in data:
    print(document)