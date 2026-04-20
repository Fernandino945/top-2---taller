#!/usr/bin/env python3
"""
MQTT Sensor Simulator for Agricultural IoT System
Publishes temperature and humidity data to topic: campo/<zona>/sensores
QoS Level: 1 (At least once)
"""

import os
import json
import time
import random
import paho.mqtt.client as mqtt


# Configuration from environment variables
SENSOR_ID = os.getenv("SENSOR_ID", "0")
ZONA = os.getenv("ZONA", "general")
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC = f"campo/{ZONA}/sensores"

# MQTT Client instance
client = None


def on_connect(client, userdata, flags, rc):
    """Callback when client connects to broker"""
    if rc == 0:
        print(f"[Sensor {SENSOR_ID}] Conectado al broker en {MQTT_BROKER}:{MQTT_PORT}")
        print(f"[Sensor {SENSOR_ID} / {ZONA}] Topic: {TOPIC}")
    else:
        print(f"[Sensor {SENSOR_ID}] Error de conexión, código: {rc}")


def on_disconnect(client, userdata, rc):
    """Callback when client disconnects"""
    if rc != 0:
        print(f"[Sensor {SENSOR_ID}] Desconexión inesperada, código: {rc}")


def on_publish(client, userdata, mid):
    """Callback when message is published"""
    pass  # Silent on success


def publish_sensor_data():
    """Generate and publish sensor data"""
    global client

    # Create MQTT client
    client = mqtt.Client(client_id=f"sensor-{SENSOR_ID}")
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    # Connect to broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    except Exception as e:
        print(f"[Sensor {SENSOR_ID}] Error al conectar: {e}")
        return

    # Start network loop (non-blocking)
    client.loop_start()

    # Allow connection to establish
    time.sleep(2)

    # Publish sensor data in loop
    try:
        while True:
            # Generate random sensor data
            temperatura = round(random.uniform(10, 35), 2)
            humedad = round(random.uniform(30, 90), 2)

            data = {
                "sensor_id": SENSOR_ID,
                "zona": ZONA,
                "temperatura": temperatura,
                "humedad": humedad
            }

            # Publish with QoS 1 (At least once)
            result = client.publish(TOPIC, json.dumps(data), qos=1)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[Sensor {SENSOR_ID} / {ZONA}] Enviado: {json.dumps(data)}")
            else:
                print(f"[Sensor {SENSOR_ID}] Error al enviar: {result.rc}")

            # Wait 3 seconds before next publish
            time.sleep(3)

    except KeyboardInterrupt:
        print(f"[Sensor {SENSOR_ID}] Deteniendo...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    publish_sensor_data()
