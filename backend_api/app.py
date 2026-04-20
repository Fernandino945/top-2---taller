#!/usr/bin/env python3
"""
Flask REST API for Agricultural IoT System
Endpoints:
  GET /logs - All zones latest 20 readings
  GET /logs/<zona> - Specific zone latest 20 readings
  GET /zonas - List of unique zones
"""

import os
from flask import Flask, jsonify
from pymongo import MongoClient, DESCENDING
from datetime import datetime


app = Flask(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/")
MONGODB_DB = "agro_iot"
MONGODB_COLLECTION = "lecturas"

# MongoDB client
mongo_client = None
coleccion = None


def init_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, coleccion
    max_retries = 5
    for intento in range(max_retries):
        try:
            mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            mongo_client.admin.command('ping')
            db = mongo_client[MONGODB_DB]
            coleccion = db[MONGODB_COLLECTION]
            print(f"[API] MongoDB connectado: {MONGODB_URI}")
            return True
        except Exception as e:
            print(f"[API] Intento {intento + 1}/{max_retries} - Error: {e}")
            if intento < max_retries - 1:
                import time
                time.sleep(2)
    return False


@app.route('/logs', methods=['GET'])
def logs():
    """Get latest 20 readings from all zones"""
    try:
        docs = list(
            coleccion.find({}, {"_id": 0})
            .sort("timestamp", DESCENDING)
            .limit(20)
        )
        return jsonify(docs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/logs/<zona>', methods=['GET'])
def logs_por_zona(zona):
    """Get latest 20 readings from specific zone"""
    try:
        docs = list(
            coleccion.find({"zona": zona}, {"_id": 0})
            .sort("timestamp", DESCENDING)
            .limit(20)
        )
        return jsonify(docs), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/zonas', methods=['GET'])
def zonas():
    """Get list of unique zones with data"""
    try:
        resultado = coleccion.distinct("zona")
        return jsonify(sorted(resultado)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Initialize MongoDB connection
    if not init_mongodb():
        print("[API] Error: No se pudo conectar a MongoDB")
        exit(1)

    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)
