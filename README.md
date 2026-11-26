# PortEdge — Edge Computing Platform for Smart Port Operations

**Computer Engineering Portfolio Project**  
Designed for real-world logistics environments such as **Jeddah Islamic Port** and Saudi Vision 2030 smart logistics initiatives.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![MQTT](https://img.shields.io/badge/protocol-MQTT-green.svg)

PortEdge is a complete **edge-to-cloud** simulation and monitoring platform that demonstrates core Computer Engineering skills:

- Real-time systems & concurrent data processing
- IoT protocols (MQTT with QoS)
- Edge AI / lightweight anomaly detection
- Sensor data pipelines & digital twins
- Networked systems design
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
- Integrate computer vision concepts for cargo inspection
- Build production-grade observability

---

## Architecture

```
┌─────────────────┐     MQTT      ┌──────────────────────┐
│ Sensor          │ ─────────────► │   Edge Gateway       │
│ Simulators      │   (QoS 1)     │  - Rule engine       │
│ (Temp, Vib,     │               │  - Anomaly detection │
│  GPS, Door...)  │               │  - Local buffer      │
└─────────────────┘               │  - Health checks     │
                                  └──────────┬───────────┘
                                             │ REST / WebSocket
┌─────────────────┐                          ▼
│ Computer Vision │               ┌──────────────────────┐
│ (Cargo Inspect) │◄──────────────│   Dashboard + API    │
└─────────────────┘               │  - Real-time view    │
                                  │  - Alerts            │
                                  │  - Metrics           │
                                  └──────────────────────┘
```

**Key design decisions (Computer Engineering focus):**
- Edge-first processing (reduce cloud dependency & latency)
- MQTT for lightweight, reliable messaging under constrained bandwidth
- Stateless + local state hybrid for resilience
- Clear separation of concerns between simulation, edge logic, and presentation

---

## Features

- **Multi-sensor digital twin** — Container temperature (reefer), vibration (crane/yard equipment), GPS, door status, humidity
- **Edge Gateway** — Receives MQTT messages, runs lightweight anomaly detection (statistical + Isolation Forest style), buffers data, exposes REST API
- **Real-time Dashboard** — Live metrics, alerts, sensor health
- **Computer Vision placeholder** — Simulated cargo damage / seal inspection pipeline
- **Full Docker Compose stack** — One-command startup
- **Observability** — Structured logging, health endpoints, basic metrics
- **Extensible** — Easy to add new sensor types or ML models

---

## Technology Stack

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| Language           | Python 3.11+                        |
| Messaging          | MQTT (Eclipse Mosquitto)            |
| Edge Logic         | FastAPI + asyncio + scikit-learn    |
| Dashboard          | Streamlit + Plotly                  |
| Containerization   | Docker + Docker Compose             |
| Data               | In-memory + optional SQLite         |
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
- Edge Gateway API: http://localhost:8000
- Dashboard: http://localhost:8501
- MQTT Broker: localhost:1883
- API Docs: http://localhost:8000/docs

---

## Project Structure

```
portedge/
├── README.md
├── docker-compose.yml
├── services/
│   ├── edge-gateway/          # Core edge processing
│   ├── sensor-simulator/      # Generates realistic sensor streams
│   └── dashboard/             # Visualization & control
├── infrastructure/
│   └── mosquitto/             # MQTT config
├── docs/
└── scripts/
```

---

## Computer Engineering Skills Demonstrated

- Concurrent systems (asyncio, multi-producer/consumer)
- Network protocols & reliability (MQTT QoS, reconnection)
- Edge computing patterns (local inference, buffering, fail-over)
- Real-time data pipelines
- Systems design & modularity
- Container orchestration basics
- Observability & operational readiness
- Applied ML on constrained environments

---

## Roadmap / Iterations

We will improve this project iteratively:

1. ✅ Initial structure + core MQTT + edge gateway
2. Robust anomaly detection + alerting
3. Computer vision cargo inspection module
4. Persistence layer + historical analytics
5. Security (TLS MQTT, API auth)
6. Performance testing & optimization
7. Kubernetes manifests (optional)
8. Full CI pipeline + tests

---

## License

MIT License — see [LICENSE](LICENSE)

---

**Built as a Computer Engineering portfolio project focused on Jeddah / Red Sea logistics and Vision 2030 smart infrastructure.**

Made by [Wasim Chami](https://github.com/wasim-505)
