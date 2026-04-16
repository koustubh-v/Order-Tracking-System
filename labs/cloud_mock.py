
import os
import shutil

class CloudSimulation:
    def __init__(self, provider="AWS"):
        self.provider = provider
        self.storage_root = f"./cloud_storage_{provider.lower()}/"
        os.makedirs(self.storage_root, exist_ok=True)
        print(f"☁️  Cloud Service Provider: {provider} initialized (Task 24)")

    def upload_file(self, local_path, cloud_dest):
        dest_path = os.path.join(self.storage_root, cloud_dest)
        shutil.copy(local_path, dest_path)
        print(f"📤 Uploaded to {self.provider} Storage: {cloud_dest}")

    def run_pipeline_on_compute(self, script_name):
        print(f"⚙️  Provisioning {self.provider} Compute Instance (EC2/GCE)...")
        print(f"▶️  Executing data pipeline {script_name} in cloud environment.")
        print("✅ Compute job finished.")

    def run_bigquery_analysis(self, query):
        print(f"📊 Running Warehouse Analysis on {self.provider} (BigQuery/Redshift)...")
        print(f"🔍 Query: {query}")
        print("✅ Analysis returned result set.")

def compare_clouds():
    print("\n--- Cloud Service Comparison (Task 24) ---")
    print("| Service    | AWS        | GCP           | Azure       |")
    print("|------------|------------|---------------|-------------|")
    print("| Storage    | S3         | GCS           | Blob        |")
    print("| Compute    | EC2        | Compute Engine| VM          |")
    print("| Data Whse  | Redshift   | BigQuery      | Synapse     |")
    print("| Serverless | Lambda     | Cloud Func    | Azure Func  |")

if __name__ == "__main__":
    compare_clouds()
    
    sim = CloudSimulation("AWS")
    
    if os.path.exists("cleaned_combined_products.csv"):
        sim.upload_file("cleaned_combined_products.csv", "raw/amazon_products.csv")
        
    sim.run_pipeline_on_compute("spark_lab.py") # Task 26
    sim.run_bigquery_analysis("SELECT SUM(revenue) FROM orders") # Task 27
