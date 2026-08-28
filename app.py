import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from groq import Groq, GroqError
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Paste your MongoDB Atlas connection string here before running the app.
MONGODB_URI = "mongodb+srv://vuranagamanisusmitha_db_user:susmithavura@cluster0.p3g9ekh.mongodb.net/?appName=Cluster0"

# MongoClient connects when the app first performs a database operation.
mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
database = mongo_client["life_navigator"]


@app.route("/")
def home():
    return send_from_directory(app.root_path, "index.html")


@app.route("/style.css")
def stylesheet():
    return send_from_directory(app.root_path, "style.css")


@app.route("/script.js")
def javascript():
    return send_from_directory(app.root_path, "script.js")


@app.route("/api/test")
def test():
    return jsonify({
        "status": "success",
        "message": "Flask backend is connected!"
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip() if isinstance(data.get("message", ""), str) else ""

    if not message:
        return jsonify({"error": "A message is required."}), 400

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "GROQ_API_KEY is not configured."}), 500

    try:
        client = Groq(api_key=api_key)
        result = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": message}]
        )
        return jsonify({"response": result.choices[0].message.content})
    except GroqError:
        return jsonify({"error": "The AI service could not process the request."}), 502


@app.route("/db-test")
def database_test():
    try:
        database.command("ping")
        return jsonify({"status": "MongoDB connected"})
    except PyMongoError as e:
        print("MONGODB ERROR:", e)
        return jsonify({
            "status": "MongoDB connection failed",
            "error": str(e)
        }), 503


if __name__ == "__main__":
    app.run(debug=True)