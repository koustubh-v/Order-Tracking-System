import json
import os
import time
from datetime import datetime, timezone
from kafka import KafkaConsumer
import db

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

def main():
    db.init_db()
    
    while True:
        try:
            consumer = KafkaConsumer(
                "order_events",
                bootstrap_servers=KAFKA_BROKER,
                group_id="data-pipeline-group",
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            print(f"Connected to Kafka broker at {KAFKA_BROKER}")
            break
        except Exception as e:
            print(f"Waiting for Kafka... {e}")
            time.sleep(2)

    # Dictionary to keep track of placed timestamps for delivery metric
    order_start_times = {}

    print("Listening for events...")
    for message in consumer:
        event = message.value
        print(f"Received event: {event}")
        
        try:
            # Parse timestamp and derive hour bucket
            dt = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
            hour_bucket = dt.replace(minute=0, second=0, microsecond=0).isoformat()
            
            # Store in order_analytics
            db.insert_analytics(event, hour_bucket)
            
            # Track delivery time metric
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
