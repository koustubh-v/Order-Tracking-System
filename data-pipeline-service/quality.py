import statistics

def check_anomaly(current_value, history):
    if len(history) < 5:
        return False, 0.0
        
    mean = statistics.mean(history)
    stdev = statistics.stdev(history) if len(history) > 1 else 0.0
    
    if stdev == 0:
        return current_value > mean * 2, 0.0
        
    z_score = (current_value - mean) / stdev
    is_anomaly = abs(z_score) > 3
    
    return is_anomaly, z_score

def validate_schema(data, schema):
    for key, expected_type in schema.items():
        if key not in data:
            return False, f"Missing key: {key}"
        if not isinstance(data[key], expected_type):
            return False, f"Invalid type for {key}: expected {expected_type}"
    return True, "Success"
