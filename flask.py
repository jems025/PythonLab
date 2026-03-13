from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
import datetime

app = Flask(__name__)


app.config["MONGO_URI"] = "<your-mongodb-connection-string>"

mongo_client = MongoClient(app.config["MONGO_URI"])
db = mongo_client.bookmark_manager
bookmarks_collection = db.bookmarks


def serialize_bookmark(bookmark):
    bookmark['_id'] = str(bookmark['_id'])
    return bookmark

@app.route("/")
def home():
    return "Bookmark Manager API is running. Use /add_bookmark and /bookmarks/<tag> endpoints."


@app.route("/add_bookmark", methods=["POST"])
def add_bookmark():
    data = request.get_json()
    if not data or 'url' not in data or 'title' not in data:
        return jsonify({"error": "Missing title or URL"}), 400

    bookmark = {
        "title": data["title"],
        "url": data["url"],
        "tags": data.get("tags", []), # Expects a list of tags
        "created_at": datetime.datetime.utcnow()
    }
    
    result = bookmarks_collection.insert_one(bookmark)
    return jsonify({"message": "Bookmark added successfully", "id": str(result.inserted_id)}), 201


@app.route("/bookmarks/<tag>", methods=["GET"])
def get_bookmarks_by_tag(tag):
   
    found_bookmarks = bookmarks_collection.find({"tags": tag})
    
    bookmarks_list = [serialize_bookmark(bookmark) for bookmark in found_bookmarks]
    
    return jsonify(bookmarks_list), 200

if __name__ == "__main__":
   
    try:
        mongo_client.admin.command('ping')
        print("MongoDB connected successfully!")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
    
    app.run(debug=True)

