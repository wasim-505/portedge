"""
PortEdge Sensor Simulator
=========================
Generates realistic multi-sensor streams for a smart port environment.
Simulates reefer containers, crane vibration, GPS trackers, door sensors, etc.
"""

import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from typing import Dict, Any

import numpy as np
import paho.mqtt.client as mqtt

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "2.0"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("sensor-simulator")

# ---------------------------------------------------------------------------
# Sensor definitions (Jeddah Port style)
# ---------------------------------------------------------------------------
SENSORS = [
    # Reefer containers (temperature critical)
    {"id": "reefer-JED-001", "type": "temperature", "unit": "°C", "base": -18.0, "noise": 0.4, "location": "Yard-A3"},
    {"id": "reefer-JED-002", "type": "temperature", "unit": "°C", "base": -22.0, "noise": 0.5, "location": "Yard-A3"},
    {"id": "reefer-JED-003", "type": "temperature", "unit": "°C", "base": 4.0, "noise": 0.3, "location": "Yard-B1"},
    # Crane / RTG vibration (predictive maintenance)
    {"id": "crane-RTG-12", "type": "vibration", "unit": "mm/s", "base": 2.1, "noise": 0.3, "location": "Berth-3"},
    {"id": "crane-STS-07", "type": "vibration", "unit": "mm/s", "base": 1.8, "noise": 0.25, "location": "Berth-1"},
    # Humidity
    {"id": "hum-Yard-A", "type": "humidity", "unit": "%", "base": 65.0, "noise": 3.0, "location": "Yard-A"},
    # Door / seal status (0=closed, 1=open)
    {"id": "door-CNT-88421", "type": "door_status", "unit": "state", "base": 0.0, "noise": 0.0, "location": "Gate-2"},
    # GPS-ish (simulated speed for moving assets)
    {"id": "tractor-ETT-05", "type": "speed", "unit": "km/h", "base": 12.0, "noise": 4.0, "location": "Internal-Road"},
]


def generate_value(sensor: Dict[str, Any], tick: int) -> float:
    """Generate a realistic value with occasional anomalies."""
    base = sensor["base"]
    noise = sensor["noise"]
    value = base + np.random.normal(0, noise)

    # Inject anomalies ~3% of the time to exercise edge detection
    if random.random() < 0.03:
        if sensor["type"] == "temperature":
            value = base + random.choice([-8.0, 12.0])
        elif sensor["type"] == "vibration":
            value = base * random.uniform(3.5, 6.0)
        elif sensor["type"] == "humidity":
            value = random.uniform(90, 99)
        elif sensor["type"] == "door_status":
            value = 1.0
        elif sensor["type"] == "speed":
            value = random.uniform(40, 55)

    if sensor["type"] == "humidity":
        value = max(0.0, min(100.0, value))
    if sensor["type"] == "door_status":
        value = 1.0 if value > 0.5 else 0.0

    return round(float(value), 3)


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        logger.info(f"Simulator connected to MQTT at {MQTT_HOST}:{MQTT_PORT}")
    else:
        logger.error(f"MQTT connect failed: {reason_code}")


def main():
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="portedge-sensor-simulator",
    )
    client.on_connect = on_connect

    for attempt in range(12):
        try:
            client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            break
        except Exception as e:
            logger.warning(f"MQTT connect attempt {attempt+1} failed: {e}")
            time.sleep(3)
    else:
        logger.error("Could not connect to MQTT after retries. Exiting.")
        return

    client.loop_start()
    logger.info(f"Starting sensor simulation (interval={PUBLISH_INTERVAL}s)...")
    logger.info(f"Publishing {len(SENSORS)} sensors")

    tick = 0
    try:
        while True:
            now = datetime.now(timezone.utc).isoformat()
            for sensor in SENSORS:
                value = generate_value(sensor, tick)
                payload = {
                    "sensor_id": sensor["id"],
                    "sensor_type": sensor["type"],
                    "value": value,
                    "unit": sensor["unit"],
                    "timestamp": now,
                    "location": sensor.get("location"),
                    "metadata": {
                        "tick": tick,
                        "simulated": True,
                        "port": "Jeddah Islamic Port",
                    },
                }
                topic = f"portedge/sensors/{sensor['type']}/{sensor['id']}"
                client.publish(topic, json.dumps(payload), qos=1)
            tick += 1
            if tick % 30 == 0:
                logger.info(f"Published {tick * len(SENSORS)} total readings")
            time.sleep(PUBLISH_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
