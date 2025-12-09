# brain/mongodb.py
from pymongo import MongoClient

# For local MongoDB
client = MongoClient("mongodb://localhost:27017/")

# For MongoDB Atlas
# client = MongoClient("mongodb+srv://<username>:<password>@cluster0.mongodb.net/<dbname>?retryWrites=true&w=majority")

db = client["BrainDiseaseDB"]  # Database name
brain_collection = db["brain_data"]  # Collection name
