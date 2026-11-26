"""
PortEdge Edge Gateway
=====================
Real-time MQTT consumer + lightweight edge AI anomaly detection.
Demonstrates concurrent systems, networking reliability, and edge computing.
"""

import asyncio
import json
import logging
import os
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Optional

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sklearn.ensemble import IsolationForest
import paho.mqtt.client as mqtt

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MQTT_HOST = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SENSOR_TOPIC = "portedge/sensors/#"
WINDOW_SIZE = 30
ANOMALY_CONTAMINATION = 0.08
RECONNECT_DELAY = 5

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("edge-gateway")

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------
class SensorReading(BaseModel):
    sensor_id: str
    sensor_type: str
    value: float
    unit: str
    timestamp: str
    location: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Alert(BaseModel):
    id: str
    sensor_id: str
    sensor_type: str
    severity: str
    message: str
    value: float
    timestamp: str
    score: float


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    mqtt_connected: bool
    sensors_seen: int
    total_readings: int
    active_alerts: int
    version: str = "0.2.0"


# ---------------------------------------------------------------------------
# Edge state (thread-safe)
# ---------------------------------------------------------------------------
class EdgeState:
    def __init__(self):
        self.start_time = time.time()
        self.mqtt_connected = False
        self.readings: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=WINDOW_SIZE))
        self.latest: Dict[str, SensorReading] = {}
        self.alerts: Deque[Alert] = deque(maxlen=200)
        self.total_readings = 0
        self.models: Dict[str, IsolationForest] = {}
        self._lock = threading.Lock()  # used from MQTT thread + asyncio

    def get_or_create_model(self, sensor_id: str) -> IsolationForest:
        if sensor_id not in self.models:
            self.models[sensor_id] = IsolationForest(
                contamination=ANOMALY_CONTAMINATION,
                random_state=42,
                n_estimators=50,
            )
        return self.models[sensor_id]


state = EdgeState()

# Global event loop reference for safe scheduling from MQTT thread
_main_loop: Optional[asyncio.AbstractEventLoop] = None


# ---------------------------------------------------------------------------
# Anomaly detection (edge AI)
# ---------------------------------------------------------------------------
def detect_anomaly(sensor_id: str, value: float) -> Optional[float]:
    """Lightweight statistical + IsolationForest anomaly score."""
    window = state.readings[sensor_id]
    window.append(value)

    if len(window) < 10:
        return None

    data = np.array(window).reshape(-1, 1)
    model = state.get_or_create_model(sensor_id)

    if len(window) % 5 == 0:
        try:
            model.fit(data)
        except Exception as e:
            logger.warning(f"Model fit failed for {sensor_id}: {e}")
            return None

    try:
        score = -model.decision_function([[value]])[0]
        return float(score)
    except Exception:
        mean = float(np.mean(data))
        std = float(np.std(data)) + 1e-6
        return abs(value - mean) / std


def severity_from_score(score: float) -> str:
    if score > 3.5:
        return "critical"
    if score > 2.5:
        return "high"
    if score > 1.8:
        return "medium"
    return "low"


def process_reading_sync(reading: SensorReading) -> None:
    """Process a reading safely from any thread."""
    with state._lock:
        state.latest[reading.sensor_id] = reading
        state.total_readings += 1

        score = detect_anomaly(reading.sensor_id, reading.value)
        if score is not None and score > 1.5:
            sev = severity_from_score(score)
            alert = Alert(
                id=f"{reading.sensor_id}-{int(time.time() * 1000)}",
                sensor_id=reading.sensor_id,
                sensor_type=reading.sensor_type,
                severity=sev,
                message=(
                    f"Anomalous {reading.sensor_type} reading: "
                    f"{reading.value:.2f} {reading.unit} (score={score:.2f})"
                ),
                value=reading.value,
                timestamp=reading.timestamp,
                score=score,
            )
            state.alerts.appendleft(alert)
            logger.warning(f"ALERT [{sev.upper()}] {alert.message}")


# ---------------------------------------------------------------------------
# MQTT callbacks (run in paho thread)
# ---------------------------------------------------------------------------
def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        state.mqtt_connected = True
        logger.info(f"Connected to MQTT broker at {MQTT_HOST}:{MQTT_PORT}")
        client.subscribe(SENSOR_TOPIC, qos=1)
        logger.info(f"Subscribed to {SENSOR_TOPIC}")
    else:
        state.mqtt_connected = False
        logger.error(f"MQTT connection failed with code {reason_code}")


def on_disconnect(client, userdata, reason_code, properties=None):
    state.mqtt_connected = False
    logger.warning(f"Disconnected from MQTT (code={reason_code}). Will attempt reconnect...")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        reading = SensorReading(**payload)
        process_reading_sync(reading)
    except Exception as e:
        logger.error(f"Failed to process message on {msg.topic}: {e}")


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="PortEdge Edge Gateway",
    description="Real-time edge processing for smart port IoT sensors",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

mqtt_client: Optional[mqtt.Client] = None


def _create_mqtt_client() -> mqtt.Client:
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id="portedge-edge-gateway",
    )
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    return client


@app.on_event("startup")
async def startup():
    global mqtt_client, _main_loop
    _main_loop = asyncio.get_running_loop()
    logger.info("Starting PortEdge Edge Gateway v0.2.0...")

    mqtt_client = _create_mqtt_client()

    # Retry connection with backoff
    for attempt in range(1, 13):
        try:
            mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
            mqtt_client.loop_start()
            logger.info("MQTT loop started")
            break
        except Exception as e:
            logger.warning(f"MQTT connect attempt {attempt}/12 failed: {e}")
            await asyncio.sleep(RECONNECT_DELAY)
    else:
        logger.error("Could not connect to MQTT after multiple attempts")


@app.on_event("shutdown")
async def shutdown():
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
    logger.info("Edge Gateway shut down")


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok" if state.mqtt_connected else "degraded",
        uptime_seconds=round(time.time() - state.start_time, 1),
        mqtt_connected=state.mqtt_connected,
        sensors_seen=len(state.latest),
        total_readings=state.total_readings,
        active_alerts=len(state.alerts),
    )


@app.get("/sensors")
async def list_sensors():
    with state._lock:
        sensors = [
            {
                "sensor_id": r.sensor_id,
                "type": r.sensor_type,
                "value": r.value,
                "unit": r.unit,
                "timestamp": r.timestamp,
                "location": r.location,
            }
            for r in state.latest.values()
        ]
    return {"count": len(sensors), "sensors": sensors}


@app.get("/sensors/{sensor_id}")
async def get_sensor(sensor_id: str):
    with state._lock:
        if sensor_id not in state.latest:
            return {"error": "sensor not found"}
        return state.latest[sensor_id].model_dump()


@app.get("/alerts")
async def get_alerts(limit: int = 50):
    with state._lock:
        alerts = [a.model_dump() for a in list(state.alerts)[:limit]]
    return {"count": len(alerts), "alerts": alerts}


@app.get("/")
async def root():
    return {
        "service": "PortEdge Edge Gateway",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            with state._lock:
                payload = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sensors": {k: v.model_dump() for k, v in state.latest.items()},
                    "alerts": [a.model_dump() for a in list(state.alerts)[:10]],
                }
            await websocket.send_json(payload)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
