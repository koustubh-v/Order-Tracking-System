# Order Tracking and Analytics System

A distributed, real-time data engineering platform designed to ingest, process, and visualize e-commerce order events at scale. The system utilizes a modern technology stack to demonstrate a complete end-to-end data pipeline, from event generation to a live star-schema warehouse.

## Architecture Overview

The system is composed of several microservices coordinated via Docker Compose:

1.  **Order API**: A FastAPI-based entry point that receives order requests and publishes them to a Kafka topic.
2.  **Infrastructure (Kafka & Zookeeper)**: Serves as the distributed event backbone, ensuring decoupled communication between services.
3.  **Order Processor**: A Python service that simulates order lifecycle state changes (Placed -> Packed -> Shipped -> Delivered).
4.  **Data Pipeline Service**: The core ETL/ELT engine that consumes raw events, performs data quality checks, normalizes prices, and loads data into a Star Schema.
5.  **Analytics Backend**: A Node.js service that provides RESTful endpoints for complex queries and uses Socket.io to push real-time updates to the frontend.
6.  **Dashboard**: A React-based visualization interface for real-time monitoring of sales trends, category distribution, and system performance.
7.  **PostgreSQL**: The central data warehouse implementing a Star Schema design (Fact and Dimension tables).

## Key Features

### Star Schema Data Warehouse
The database is structured to support high-performance analytical queries:
*   **Fact Orders**: Contains transactional data including order IDs, user IDs, amounts, and foreign keys to dimensions.
*   **Dimension Time**: Supports granular time-based analysis (hour, day, month, year, weekday).
*   **Dimension Products**: Integrated with a subset of the Amazon Products Dataset (50,000+ records) to provide rich categorical metadata.

### Real-Time Analytics
*   **Window Functions**: The system calculates running totals and moving averages in real-time.
*   **ELT Pipeline**: Implements an Extract-Load-Transform pattern by staging raw JSON payloads before structured ingestion.
*   **Data Quality**: Integrated Z-Score anomaly detection to identify price spikes or fraudulent patterns during ingestion.

## Getting Started

### Prerequisites
*   Docker and Docker Compose
*   Python 3.11+ (for local simulations)

### Installation and Execution

1.  **Clone the Repository**:
    ```bash
    git clone [repository-url]
    cd real-orders
    ```

2.  **Launch the System**:
    Start all microservices in detached mode:
    ```bash
    docker-compose up --build -d
    ```

3.  **Bootstrap Data**:
    The system automatically seeds the Dimension tables from the included `cleaned_combined_products.csv` on the first startup of the `data-pipeline-service`.

4.  **Simulate Traffic**:
    Run the order generator to feed the pipeline:
    ```bash
    python3 generate_orders.py
    ```

### Accessing the Platform
*   **Live Dashboard**: http://localhost:5173
*   **Analytics API**: http://localhost:4000
*   **Order API**: http://localhost:5000

## Project Structure

```text
├── analytics-backend/    # Node.js API with Socket.io
├── dashboard/            # React/Vite Frontend
├── data-pipeline-service/ # Python ETL/ELT Service
├── src/
│   ├── order-api/        # FastAPI Entry point
│   └── order-processor/  # Lifecycle simulator
├── labs/                 # Concept demonstrations (Spark, Airflow, etc.)
└── docker-compose.yml    # Orchestration manifest
```

## Technical Specifications
*   **Broker**: Kafka
*   **Database**: PostgreSQL 15
*   **Backend**: Python, Node.js
*   **Frontend**: React, Tailwind (Modern UI)
*   **Data Volume**: Optimized for processing hundreds of events per minute.
