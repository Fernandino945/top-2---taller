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

    # Connect to broker with retries
    max_retries = 5
    for intento in range(max_retries):
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            print(f"[Sensor {SENSOR_ID}] Conectando en intento {intento + 1}...")
            break
        except Exception as e:
            print(f"[Sensor {SENSOR_ID}] Intento {intento + 1}/{max_retries} - Error: {e}")
            if intento < max_retries - 1:
                time.sleep(2 ** intento)  # Exponential backoff
            else:
                print(f"[Sensor {SENSOR_ID}] No se pudo conectar después de {max_retries} intentos")
                return

    # Start network loop (non-blocking)
    client.loop_start()

    # Allow connection to establish
    time.sleep(2)

    # Publish sensor data in loop
    consecutive_errors = 0
    try:
        while True:
            # Check if still connected
            if not client.is_connected():
                print(f"[Sensor {SENSOR_ID}] Desconectado, intentando reconectar...")
                try:
                    client.reconnect()
                    consecutive_errors = 0
                except Exception as e:
                    print(f"[Sensor {SENSOR_ID}] Error al reconectar: {e}")
                    consecutive_errors += 1
                    if consecutive_errors > 10:
                        print(f"[Sensor {SENSOR_ID}] Demasiados errores de reconexión, esperando 5s...")
                        time.sleep(5)
                        consecutive_errors = 0
                    time.sleep(2)
                    continue
            
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
            try:
                result = client.publish(TOPIC, json.dumps(data), qos=1)

                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    print(f"[Sensor {SENSOR_ID} / {ZONA}] Enviado: {json.dumps(data)}")
                    consecutive_errors = 0
                else:
                    print(f"[Sensor {SENSOR_ID}] Error al enviar: {result.rc}")
                    consecutive_errors += 1
            except Exception as e:
                print(f"[Sensor {SENSOR_ID}] Excepción al publicar: {e}")
                consecutive_errors += 1

            # Wait 3 seconds before next publish
            time.sleep(3)

    except KeyboardInterrupt:
        print(f"[Sensor {SENSOR_ID}] Deteniendo...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    try:
        publish_sensor_data()
    except Exception as e:
        print(f"[Sensor {SENSOR_ID}] Error fatal: {e}")
        exit(1)
