
from datetime import datetime, timedelta

def extract():
    print("📥 Extracting data from Kafka/CSV...")
    return "extract_success"

def transform(status):
    print(f"🔄 Transforming data ({status})...")
    return "transform_success"

def load(status):
    print(f"📤 Loading data into PostgreSQL Star Schema ({status})...")
    return "load_success"

default_args = {
    'owner': 'college_student',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3, # Task 23: Retry mechanism
    'retry_delay': timedelta(minutes=5),
}

dag_config = {
    'dag_id': 'amazon_order_pipeline_v1',
    'schedule_interval': '@hourly', # Task 23: Scheduling
    'catchup': False,
    'tags': ['etl', 'postgres', 'spark'],
}

def simulate_dag_run():
    print(f"🚀 Executing DAG: {dag_config['dag_id']} at {datetime.now()}")
    res1 = extract()
    res2 = transform(res1)
    load(res2)
    print("✅ DAG Run Completed Successfully.")

if __name__ == "__main__":
    simulate_dag_run()
