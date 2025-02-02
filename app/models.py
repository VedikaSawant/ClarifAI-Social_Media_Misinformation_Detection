from pymongo import MongoClient, errors  # Import errors for DuplicateKeyError
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"  # Replace with your URI
DB_NAME = "misinformation_db"
COLLECTION_NAME = "fact_checks"

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Create unique index (do this ONCE, when the app starts)
    collection.create_index("content", unique=True, collation={"locale": "en", "strength": 2})  # Case-insensitive unique index
    print("Successfully connected to MongoDB and created/checked unique index.")

except Exception as e:
    print(f"Error connecting to MongoDB or creating index: {e}")
    exit()

def get_fact_check(content):
    return collection.find_one({"content": content})

def save_fact_check(content, verdict):
    try:
        result = collection.insert_one({
            "content": content,
            "verdict": verdict,
            "timestamp": datetime.utcnow()
        })
        print(f"Successfully inserted: {content} (Inserted ID: {result.inserted_id})")
    except errors.DuplicateKeyError:  # Catch DuplicateKeyError specifically
        print(f"Duplicate content, not inserted: {content}")
    except Exception as e: # Catch other errors
        print(f"Error inserting into MongoDB: {e}")