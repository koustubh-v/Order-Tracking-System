import requests
import time
import random
import uuid

API_URL = "http://localhost:5000/api/order"

def generate_order():
    user_id = f"user_{random.randint(100, 999)}"
    num_items = random.randint(1, 5)
    items = []
    
    for _ in range(num_items):
        items.append({
            "product_id": f"prod_{random.randint(1000, 9999)}",
            "quantity": random.randint(1, 3)
        })

    payload = {
        "user_id": user_id,
        "items": items
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Generated order: {response.json()['order_id']} | User: {user_id} | Amount: ${response.json()['amount']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ API down or unreachable: {e}")

if __name__ == "__main__":
    print("🚀 Starting Continuous Order Generator...")
    print("Press Ctrl+C to stop.\n")
    while True:
        generate_order()
        # Random sleep between 2 and 8 seconds
        time.sleep(random.randint(2, 8))
