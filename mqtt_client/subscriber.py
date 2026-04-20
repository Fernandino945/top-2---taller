#!/usr/bin/env python3
"""
MQTT Subscriber for Agricultural IoT System
Subscribes to: campo/+/sensores (all zones)
QoS Level: 1 (At least once)
Stores data in MongoDB
"""

import os
import json
import time
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from datetime import datetime


# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
WILDCARD_TOPIC = "campo/+/sensores"

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/")
MONGODB_DB = "agro_iot"
MONGODB_COLLECTION = "lecturas"

# MongoDB client
mongo_client = None
coleccion = None


def conectar_mongodb():
    """Establish MongoDB connection"""
    global mongo_client, coleccion
    max_retries = 5
    for intento in range(max_retries):
        try:
            mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            mongo_client.admin.command('ping')
            db = mongo_client[MONGODB_DB]
            coleccion = db[MONGODB_COLLECTION]
            print(f"[Subscriber] Conectado a MongoDB: {MONGODB_URI}")
            return True
        except Exception as e:
            print(f"[Subscriber] Intento {intento + 1}/{max_retries} - Error MongoDB: {e}")
            if intento < max_retries - 1:
                time.sleep(2)
    return False


def on_connect(client, userdata, flags, rc):
    """Callback when client connects to broker"""
    if rc == 0:
        print(f"[Subscriber] Conectado al broker en {MQTT_BROKER}:{MQTT_PORT}")
        # Subscribe with QoS 1
        client.subscribe(WILDCARD_TOPIC, qos=1)
        print(f"[Subscriber] Suscrito a: {WILDCARD_TOPIC} (QoS 1)")
    else:
        print(f"[Subscriber] Error de conexión, código: {rc}")


def on_disconnect(client, userdata, rc):
    """Callback when client disconnects"""
    if rc != 0:
        print(f"[Subscriber] Desconexión inesperada, código: {rc}")


def on_message(client, userdata, msg):
    """Callback when message is received"""
    global coleccion

    try:
        # Extract zone from topic: campo/<zona>/sensores
        topic_parts = msg.topic.split("/")
        if len(topic_parts) != 3 or topic_parts[2] != "sensores":
            print(f"[Subscriber] Topic inválido (esperado campo/[zona]/sensores): {msg.topic}")
            return

        zona = topic_parts[1]
        if not zona or zona.strip() == "":
            print(f"[Subscriber] Zona vacía en topic: {msg.topic}")
            return

        # Decode message
        try:
            payload = json.loads(msg.payload.decode())
        except json.JSONDecodeError:
            print(f"[Subscriber] Error decodificando JSON: {msg.payload}")
            return

        # Validate required fields
        if "temperatura" not in payload or "humedad" not in payload:
            print(f"[Subscriber] Payload incompleto (falta temperatura o humedad): {msg.payload}")
            return

        # Add metadata
        payload["zona"] = zona
        payload["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payload["topic"] = msg.topic
        payload["qos"] = msg.qos

        # Insert into MongoDB with error handling
        if coleccion is None:
            print(f"[{zona.upper()}] Error: MongoDB no conectado")
            return

        try:
            result = coleccion.insert_one(payload)
            print(f"[{zona.upper()}] Guardado QoS {msg.qos} | {json.dumps(payload)}")
        except Exception as db_error:
            print(f"[{zona.upper()}] Error insertando en MongoDB: {db_error}")
            # Reintentar conexión
            if not conectar_mongodb():
                print(f"[Subscriber] No se pudo reconectar a MongoDB")

    except Exception as e:
        print(f"[Subscriber] Error procesando mensaje: {e}")


def main():
    """Main subscriber loop"""
    global mongo_client

    # Connect to MongoDB first
    if not conectar_mongodb():
        print("[Subscriber] Fallido conectar a MongoDB. Abortando.")
        return

    # Create MQTT client
    client = mqtt.Client(client_id="agro-subscriber")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to MQTT broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        print(f"[Subscriber] Error al conectar a MQTT: {e}")
        return

    # Start network loop (blocking)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("[Subscriber] Deteniendo...")
    finally:
        client.disconnect()
        if mongo_client:
            mongo_client.close()


if __name__ == "__main__":
    main()
