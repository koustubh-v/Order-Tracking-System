import json
import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kafka import KafkaProducer

app = FastAPI(title="Order API")

# Setup Kafka Producer
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
_producer = None

def get_producer():
    global _producer
    if _producer is not None:
        return _producer
    try:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print(f"Connected to Kafka broker at {KAFKA_BROKER}")
        return _producer
    except Exception as e:
        print(f"Failed to connect to Kafka: {e}")
        return None

# In-memory storage
orders_db = {}

class OrderItem(BaseModel):
    product_id: str
    quantity: int

class CreateOrderRequest(BaseModel):
    user_id: str
    items: List[OrderItem]

class Order(BaseModel):
    order_id: str
    user_id: str
    status: str
    amount: float
    timestamp: str

class UpdateStatusRequest(BaseModel):
    status: str

@app.post("/api/order", response_model=Order)
def create_order(req: CreateOrderRequest):
    order_id = str(uuid.uuid4())
    
    # Calculate dummy amount based on quantity (e.g., $10 per item)
    total_amount = sum(item.quantity * 10.0 for item in req.items)
    
    timestamp = datetime.now(timezone.utc).isoformat()
    
    order = Order(
        order_id=order_id,
        user_id=req.user_id,
        status="PLACED",
        amount=total_amount,
        timestamp=timestamp
    )
    
    orders_db[order_id] = order
    
    # Emit to Kafka
    event = order.model_dump()
    prod = get_producer()
    if prod:
        prod.send("order_events", value=event)
        prod.flush()
    else:
        print("Kafka producer not initialized. Event not sent.", event)
        
    return order

@app.get("/api/order/{order_id}", response_model=Order)
def get_order(order_id: str):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]

@app.get("/api/order", response_model=List[Order])
def get_all_orders():
    return list(orders_db.values())

@app.put("/api/order/status/{order_id}")
def update_order_status(order_id: str, req: UpdateStatusRequest):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = orders_db[order_id]
    order.status = req.status
    order.timestamp = datetime.now(timezone.utc).isoformat()
    
    # Emit update to Kafka
    event = order.model_dump()
    prod = get_producer()
    if prod:
        prod.send("order_events", value=event)
        prod.flush()
        
    return {"message": "Status updated"}
