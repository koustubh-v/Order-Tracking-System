import os
import time
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://postgres:postgres@postgres:5432/analytics")

def get_connection():
    while True:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            print(f"Waiting for PostgreSQL... {e}")
            time.sleep(2)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS order_analytics (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            amount NUMERIC(10, 2) NOT NULL,
            event_time TIMESTAMP NOT NULL,
            hour_bucket TIMESTAMP NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS delivery_metrics (
            order_id VARCHAR(255) PRIMARY KEY,
            delivery_time_seconds INT NOT NULL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def insert_analytics(event_data, hour_bucket):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO order_analytics (order_id, user_id, status, amount, event_time, hour_bucket)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (
        event_data['order_id'],
        event_data['user_id'],
        event_data['status'],
        event_data['amount'],
        event_data['timestamp'],
        hour_bucket
    ))
    
    conn.commit()
    cur.close()
    conn.close()

def insert_delivery_metric(order_id, delivery_time_seconds):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO delivery_metrics (order_id, delivery_time_seconds)
        VALUES (%s, %s)
        ON CONFLICT (order_id) DO UPDATE SET delivery_time_seconds = EXCLUDED.delivery_time_seconds
    ''', (order_id, delivery_time_seconds))
    
    conn.commit()
    cur.close()
    conn.close()
