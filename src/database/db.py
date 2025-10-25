import chromadb
from datetime import datetime
import json
import uuid
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "restaurant_data")
client = chromadb.PersistentClient(path=db_path)
collection = client.get_or_create_collection("restaurants")

def create_restaurant(name: str) -> str:
    key = str(uuid.uuid4())
    collection.add(
        ids=[f"{key}_restaurant"],
        documents=[json.dumps({"name": name, "tables": 10})],
        metadatas=[{"type": "restaurant", "key": key, "name": name, "timestamp": datetime.now().isoformat()}]
    )
    return key

def log_event(key: str, event_type: str, data: dict):
    event_id = str(uuid.uuid4())
    collection.add(
        ids=[event_id],
        documents=[json.dumps(data)],
        metadatas={"type": event_type, "key": key, "timestamp": datetime.now().isoformat()}
    )

def get_restaurant(key: str) -> dict:
    results = collection.get(where={"$and": [{"type": "restaurant"}, {"key": key}]})
    if results["ids"]:
        return json.loads(results["documents"][0])
    return None

def get_events(key: str, event_type: str = None) -> list:
    where = {"key": key}
    if event_type:
        where = {"$and": [{"key": key}, {"type": event_type}]}
    results = collection.get(where=where)
    return [{"data": json.loads(doc), "meta": meta} for doc, meta in zip(results["documents"], results["metadatas"])]

def list_restaurants() -> list:
    results = collection.get(where={"type": "restaurant"})
    return [{"key": meta["key"], "name": meta["name"]} for meta in results["metadatas"]]
