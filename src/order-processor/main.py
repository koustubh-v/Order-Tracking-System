import json
import os
import time
import requests
from datetime import datetime, timezone
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
ORDER_API_URL = os.getenv("ORDER_API_URL", "http://order-api:5000")

def main():
    while True:
        try:
            consumer = KafkaConsumer(
                "order_events",
                bootstrap_servers=KAFKA_BROKER,
                group_id="order-processor-group",
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKER,
                value_serializer=lambda x: json.dumps(x).encode('utf-8')
            )
            print(f"Connected to Kafka broker at {KAFKA_BROKER}")
            break
        except Exception as e:
            print(f"Waiting for Kafka... {e}")
            time.sleep(2)

    for message in consumer:
        event = message.value
        status = event.get("status")
        

        if status == "PLACED":
            order_id = event["order_id"]
            

            print(f"Processing Order {order_id}...")
            transitions = ["PACKED", "SHIPPED", "DELIVERED"]
            
            for next_status in transitions:
                time.sleep(5)
                

                updated_event = event.copy()
                updated_event["status"] = next_status
                updated_event["timestamp"] = datetime.now(timezone.utc).isoformat()
                

                try:
                    res = requests.put(
                        f"{ORDER_API_URL}/api/order/status/{order_id}",
                        json={"status": next_status}
                    )
                    if res.status_code != 200:
                        print(f"Failed to update API for {order_id}")
                except Exception as e:
                    print(f"API unreachable: {e}")
                


if __name__ == "__main__":
    main()
