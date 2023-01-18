import pymongo
import os
from dotenv import load_dotenv
load_dotenv()
mongo_user = os.getenv("MONGO_USER")
mongo_password = os.getenv("MONGO_PASSWORD")

client = pymongo.MongoClient(f"mongodb+srv://{mongo_user}:{mongo_password}@social-media-content-cr.ko9ynkb.mongodb.net/?retryWrites=true&w=majority")
db = client['linkedin']

def get_follow_bot_collection():
    return db['follow_bot']