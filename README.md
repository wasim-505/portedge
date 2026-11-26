# PortEdge — Edge Computing Platform for Smart Port Operations

**Computer Engineering Portfolio Project · v0.2**  
Designed for real-world logistics environments such as **Jeddah Islamic Port** and Saudi Vision 2030 smart logistics initiatives.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![MQTT](https://img.shields.io/badge/protocol-MQTT-green.svg)
![Version](https://img.shields.io/badge/version-0.2.0-orange.svg)

PortEdge is a complete **edge-to-cloud** simulation and monitoring platform that demonstrates core Computer Engineering skills:

- Real-time systems & concurrent data processing
- IoT protocols (MQTT with QoS + automatic reconnection)
- Edge AI / lightweight anomaly detection (Isolation Forest + statistical)
- Sensor data pipelines & digital twins
- Networked systems design & thread-safe state management
- Containerized microservices
- Observability & reliability patterns

It models the kind of edge infrastructure used in modern automated ports (container sensors, crane vibration, reefer temperature, gate cameras, etc.).

---

## Why this project matters for Jeddah / Saudi Arabia

Jeddah Islamic Port is undergoing major digital transformation (automation, electrification, IoT, AI cargo handling, predictive maintenance).  
Computer Engineers are needed to design the **edge layer** that sits between physical sensors/actuators and central cloud systems.

PortEdge shows you can:
- Design reliable real-time data paths
- Run intelligence close to the data source (edge)
- Handle unreliable networks and constrained devices
- Build production-grade observability and health checks
- Apply ML in resource-aware environments

---

## Architecture

```
┌─────────────────┐     MQTT      ┌──────────────────────┐
│ Sensor          │ ─────────────► │   Edge Gateway       │
│ Simulators      │   (QoS 1)     │  - Thread-safe state │
│ (Temp, Vib,     │               │  - Anomaly detection │
│  GPS, Door...)  │               │  - Auto-reconnect   │
└─────────────────┘               │  - Health checks     │
                                  └──────────┬───────────┘
                                             │ REST / WebSocket
                                             ▼
                                  ┌──────────────────────┐
                                  │   Dashboard + API    │
                                  │  - Real-time view    │
                                  │  - Alerts            │
                                  │  - Metrics           │
                                  └──────────────────────┘
```

**Key design decisions (Computer Engineering focus):**
- Edge-first processing (reduce cloud dependency & latency)
- MQTT for lightweight, reliable messaging under constrained bandwidth
- Thread-safe shared state between MQTT callback thread and FastAPI
- Automatic reconnection with backoff
- Clear separation of concerns between simulation, edge logic, and presentation

---

## Features (v0.2)

- **Multi-sensor digital twin** — Reefer temperature, crane vibration, humidity, door status, electric tractor speed (Jeddah-inspired IDs)
- **Edge Gateway** — MQTT consumer with QoS 1, sliding-window buffering, IsolationForest + z-score anomaly detection, thread-safe state, REST + WebSocket APIs
- **Real-time Dashboard** — Live metrics, alerts, sensor table and charts
- **Robustness** — Connection retry with backoff, structured logging, health endpoint
- **Full Docker Compose stack** — One-command startup
- **Extensible** — Easy to add new sensor types or ML models

---

## Technology Stack

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| Language           | Python 3.11+                        |
| Messaging          | MQTT (Eclipse Mosquitto)            |
| Edge Logic         | FastAPI + scikit-learn + threading  |
| Dashboard          | Streamlit + Plotly                  |
| Containerization   | Docker + Docker Compose             |
| Protocols          | MQTT, HTTP/REST, WebSocket          |

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

```bash
git clone https://github.com/wasim-505/portedge.git
cd portedge
docker compose up --build
```

Services will be available at:
- **Dashboard**: http://localhost:8501
- **Edge Gateway API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health
- **MQTT Broker**: localhost:1883

---

## Project Structure

```
portedge/
├── README.md
├── docker-compose.yml
├── services/
│   ├── edge-gateway/          # Core edge processing (v0.2)
│   ├── sensor-simulator/      # Generates realistic sensor streams
│   └── dashboard/             # Visualization & control
├── infrastructure/
│   └── mosquitto/             # MQTT config
└── ...
```

---

## Computer Engineering Skills Demonstrated

- Concurrent systems & thread-safe shared state
- Network protocols & reliability (MQTT QoS, automatic reconnection)
- Edge computing patterns (local inference, buffering)
- Real-time data pipelines
- Systems design & modularity
- Container orchestration basics
- Observability & operational readiness
- Applied ML on constrained environments

---

## Roadmap / Iterations

1. ✅ Initial structure + core MQTT + edge gateway
2. ✅ Robust anomaly detection, thread-safety, reconnection (v0.2)
3. ⬜ Computer vision cargo inspection module
4. ⬜ Persistence layer + historical analytics
5. ⬜ Security (TLS MQTT notes, API key auth)
6. ⬜ Unit tests + GitHub Actions CI
7. ⬜ Performance notes & load testing tips
8. ⬜ Kubernetes manifests (optional)

---

## License

MIT License — see [LICENSE](LICENSE)

---

**Built as a Computer Engineering portfolio project focused on Jeddah / Red Sea logistics and Vision 2030 smart infrastructure.**

Made by [Wasim Chami](https://github.com/wasim-505)
