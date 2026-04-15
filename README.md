# Real-Time Event-Driven Order Tracking and Analytics Pipeline

This repository contains a comprehensive, event-driven data engineering platform designed to process, track, and visualize e-commerce orders in real-time. The architecture has been fully migrated from a monolithic C# setup to a robust, highly decoupled multi-service Python and Node.js infrastructure. 

The system leverages Apache Kafka for event streaming and implements an end-to-end Extract, Transform, Load (ETL) pipeline feeding into PostgreSQL, ultimately powering a real-time React dashboard with live visualization.

---

## Architectural Overview and Technology Stack

The application relies on several microservices connected via Docker networking arrays.

### 1. Central Event Bus
* **Apache Kafka & Zookeeper:** Serves as the high-throughput, low-latency messaging backbone for all inter-service communication. All state changes are broadcasted via the `order_events` topic.

### 2. Order Submission API (Python / FastAPI)
* **Directory:** `/src/order-api`
* Act as the point of ingest. It accepts HTTP `POST` requests for new orders, writes initial states to memory, and immediately pushes a `PLACED` event to Kafka. Implements lazy evaluation for resilient broker connections.

### 3. Order Processing Worker (Python)
* **Directory:** `/src/order-processor`
* Acts as a backend fulfillment simulator. It consumes `PLACED` events from Kafka and simulates sequential fulfillment lifecycle stages (`PACKED`, `SHIPPED`, `DELIVERED`), broadcasting subsequent state transitions back to Kafka at each stage.

### 4. Data Pipeline Ingestion Service (Python)
* **Directory:** `/data-pipeline-service`
* Subscribes to the Kafka event stream as a unified consumer group. It performs data transformations (deriving timestamps, hour buckets, and calculating total delivery latency) before executing strict schema insertions into the PostgreSQL data warehouse.

### 5. Analytics Data Warehouse (PostgreSQL)
* **Component:** `postgres:15`
* Stores structured analytics tracking states within the `order_analytics` table, layered alongside metric aggregation outputs in the `delivery_metrics` table. 

### 6. Analytics Backend API (Node.js / Express / Socket.io)
* **Directory:** `/analytics-backend`
* Queries PostgreSQL using `pg` to serve materialized REST aggregations (e.g. orders per hour, average delivery times).
* Implements `kafkajs` to directly consume Kafka streams, pushing real-time UI repaints to connected frontend web-clients via WebSockets.

### 7. Real-Time Dashboard (React.js / Vite)
* **Directory:** `/dashboard`
* A comprehensive browser application designed utilizing strict Vanilla CSS to accomplish a modern glassmorphism aesthetic without heavy CSS frameworks. Visualizes system states using Recharts components while maintaining an open WebSocket channel for live data mutation feeds.

---

## Installation and Execution

The entire stack is containerized, ensuring zero-dependency execution across varied environments.

### Prerequisites
* Docker
* Docker Compose
* Python 3.9+ (Optional, only required if running the generator script locally outside containerization)

### Bootstrapping the Infrastructure

Navigate to the root directory and execute Docker Compose to build and interlink all microservices securely.

```bash
docker-compose up --build -d
```

This procedure will orchestrate the initiation of Zookeeper, Kafka, PostgreSQL, the dual Python services, the Node API, and the React Dashboard. Please allow up to 30 seconds for the Kafka Broker to initialize fully and accept external producers.

---

## Verifying System Endpoints

Once Docker successfully allocates the networking grid, examine the following endpoints to verify service integrity:

* **React Live Dashboard:** http://localhost:5173
* **FastAPI Order API:** http://localhost:5000/api/order
* **Analytics Backend API:** http://localhost:4000/analytics/summary

---

## Simulating Live Traffic

To validate the real-time architectural components, a payload generation script is included. It is designed to act as a concurrent user base submitting purchases.

Open a new terminal session and execute the generator function:

```bash
# Ensure Python requests module is installed locally
pip install requests

# Execute Continuous Payload Submission
python generate_orders.py
```

### Observation Workflows

Upon initiating the generator:
1. Navigate immediately to the browser dashboard (`http://localhost:5173`).
2. New `PLACED` orders will dynamically inject into the Live Feed metrics table at the bottom of the interface.
3. Over the subsequent 15 seconds, background automated consumers (`OrderProcessor`) will pull these events, mutate their attributes, and trigger WebSockets to visually step the user status through `PACKED`, `SHIPPED`, and finally `DELIVERED`.
4. Visual distribution charts and overall delivery time metrics will calculate and synchronize implicitly without requiring HTTP browser refreshes.
