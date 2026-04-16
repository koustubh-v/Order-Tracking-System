import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

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
        CREATE TABLE IF NOT EXISTS raw_events (
            id SERIAL PRIMARY KEY,
            payload JSONB NOT NULL,
            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS dim_products (
            product_id VARCHAR(255) PRIMARY KEY,
            name TEXT NOT NULL,
            main_category VARCHAR(100),
            sub_category VARCHAR(100),
            base_price NUMERIC(10, 2)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS dim_time (
            hour_bucket TIMESTAMP PRIMARY KEY,
            day INT,
            month INT,
            year INT,
            weekday VARCHAR(20)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS fact_orders (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            product_id VARCHAR(255),
            status VARCHAR(50) NOT NULL,
            amount NUMERIC(10, 2) NOT NULL,
            event_time TIMESTAMP NOT NULL,
            hour_bucket TIMESTAMP REFERENCES dim_time(hour_bucket)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS delivery_metrics (
            order_id VARCHAR(255) PRIMARY KEY,
            delivery_time_seconds INT NOT NULL
        )
    ''')

    cur.execute('DROP TABLE IF EXISTS order_analytics CASCADE')
    cur.execute('DROP VIEW IF EXISTS order_analytics')
    
    cur.execute('''
        CREATE VIEW order_analytics AS 
        SELECT id, order_id, user_id, status, amount, event_time, hour_bucket 
        FROM fact_orders
    ''')

    conn.commit()
    cur.close()
    conn.close()

def seed_products(products_list):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.executemany('''
        INSERT INTO dim_products (product_id, name, main_category, sub_category, base_price)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO UPDATE SET
            name = EXCLUDED.name,
            main_category = EXCLUDED.main_category,
            sub_category = EXCLUDED.sub_category,
            base_price = EXCLUDED.base_price
    ''', [
        (p['product_id'], p['name'], p['main_category'], p['sub_category'], p['actual_price'])
        for p in products_list
    ])
    
    conn.commit()
    cur.close()
    conn.close()

def insert_raw_event(payload):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO raw_events (payload) VALUES (%s)', (payload,))
    conn.commit()
    cur.close()
    conn.close()

def upsert_dim_time(dt):
    hour_bucket = dt.replace(minute=0, second=0, microsecond=0)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO dim_time (hour_bucket, day, month, year, weekday)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (hour_bucket) DO NOTHING
    ''', (hour_bucket, hour_bucket.day, hour_bucket.month, hour_bucket.year, hour_bucket.strftime('%A')))
    conn.commit()
    cur.close()
    conn.close()
    return hour_bucket

def insert_fact_order(event_data, hour_bucket):
    conn = get_connection()
    cur = conn.cursor()
    
    product_id = event_data.get('items', [{}])[0].get('product_id', 'unknown') if 'items' in event_data else 'unknown'
    
    cur.execute('''
        INSERT INTO fact_orders (order_id, user_id, product_id, status, amount, event_time, hour_bucket)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        event_data['order_id'],
        event_data['user_id'],
        product_id,
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
