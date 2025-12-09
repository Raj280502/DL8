# check_mongo.py
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["BrainDiseaseDB"]
brain_collection = db["brain_data"]

for doc in brain_collection.find():
    print(doc)
