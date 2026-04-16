import json
import time
import random
import requests
import pandas as pd
import os

API_URL = "http://localhost:5000/api/order"

def get_product_data():
    csv_path = "data-pipeline-service/cleaned_combined_products.csv"
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return df[['product_id', 'actual_price']].to_dict('records')
    return None

def generate_order(product_pool):
    if product_pool:
        product = random.choice(product_pool)
        user_id = f"user_{random.randint(100, 999)}"
        items = [{"product_id": product['product_id'], "quantity": 1}]
        amount = product['actual_price'] if product['actual_price'] > 0 else random.randint(10, 150)
    else:
        user_id = f"user_{random.randint(1, 1000)}"
        items = [{"product_id": f"prod_{random.randint(1, 50)}", "quantity": random.randint(1, 3)}]
        amount = random.randint(10, 150)
        
    return {
        "user_id": user_id,
        "items": items,
        "amount": amount
    }

def main():
    print("🚀 Starting Continuous Order Generator...")
    print("Press Ctrl+C to stop.\n")
    
    product_pool = get_product_data()
    if product_pool:
        print(f"✅ Loaded {len(product_pool)} products for realistic simulation.")
    
    while True:
        try:
            order = generate_order(product_pool)
            response = requests.post(API_URL, json=order)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Generated order: {data['order_id']} | User: {data['user_id']} | Amount: ${data['amount']}")
            else:
                print(f"❌ Error: {response.text}")
                
            time.sleep(random.randint(2, 8))
        except KeyboardInterrupt:
            print("\n👋 Stopping generator...")
            break
        except Exception as e:
            print(f"⚠️ Connection error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
