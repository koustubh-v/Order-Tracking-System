import json
import os
import time
from datetime import datetime, timezone
from kafka import KafkaConsumer
import db
import transforms
import quality
import pandas as pd

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

def auto_seed():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM dim_products")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    if count == 0:
        csv_path = "cleaned_combined_products.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if 'product_id' not in df.columns:
                df['product_id'] = [f"AMZ_{i:06d}" for i in range(len(df))]
            
            products = df.head(50000)[[
                'product_id', 'name', 'main_category', 'sub_category', 'actual_price'
            ]].to_dict('records')
            db.seed_products(products)
            print("Auto-seeding complete.")
        else:
            print("Skipping auto-seed: dataset not found.")
    else:
        print(f"Database already has {count} products. Skipping seed.")

def main():
    db.init_db()
    
    try:
        auto_seed()
    except Exception as e:
        print(f"Auto-seed failed: {e}")
    
    price_history = []
    
    while True:
        try:
            consumer = KafkaConsumer(
                "order_events",
                bootstrap_servers=KAFKA_BROKER,
                group_id="data-pipeline-group",
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            break
        except Exception as e:
            time.sleep(2)

    order_start_times = {}

    for message in consumer:
        event = message.value
        db.insert_raw_event(json.dumps(event))
        
        try:
            is_valid, msg = transforms.validate_event(event)
            if not is_valid:
                continue
                
            amount = float(event['amount'])
            is_anomaly, score = quality.check_anomaly(amount, price_history)
            price_history.append(amount)
            if len(price_history) > 100: price_history.pop(0)
            
            if is_anomaly:
                print(f"ANOMALY DETECTED: Order {event['order_id']} Amount {amount}")

            event['amount_usd'] = transforms.normalize_price(amount, "USD")
            
            dt = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
            hour_bucket = db.upsert_dim_time(dt)
            
            db.insert_fact_order(event, hour_bucket)
            
            order_id = event["order_id"]
            if event["status"] == "PLACED":
                order_start_times[order_id] = dt
            elif event["status"] == "DELIVERED" and order_id in order_start_times:
                placed_time = order_start_times[order_id]
                delivery_seconds = int((dt - placed_time).total_seconds())
                db.insert_delivery_metric(order_id, delivery_seconds)
                del order_start_times[order_id]
                
        except Exception as e:
            print(f"Error processing event: {e}")

if __name__ == "__main__":
    main()
