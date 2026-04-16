def normalize_price(price, target_currency="USD"):
    if price is None: return 0.0
    rate = 83.0 if target_currency == "USD" else 1.0
    return round(float(price) / rate, 2)

def aggregate_order_metrics(items):
    total_quantity = sum(item.get('quantity', 0) for item in items)
    unique_products = len(set(item.get('product_id') for item in items))
    return {
        "total_quantity": total_quantity,
        "unique_products": unique_products
    }

def validate_event(event):
    required_fields = ['order_id', 'user_id', 'status', 'amount', 'timestamp']
    for field in required_fields:
        if field not in event:
            return False, f"Missing field: {field}"
    
    if float(event['amount']) < 0:
        return False, "Negative amount"
        
    return True, "Valid"
