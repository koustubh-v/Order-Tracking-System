
from pyspark.sql import SparkSession
import os
import shutil

def main():
    spark = SparkSession.builder \
        .appName("LakehouseLab") \
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

    from delta.tables import DeltaTable

    delta_path = "./delta_lake_storage"
    if os.path.exists(delta_path):
        shutil.rmtree(delta_path)

    print("💎 Writing data to Delta Lake (ACID compliant storage)...")
    df = spark.read.csv("cleaned_combined_products.csv", header=True, inferSchema=True).limit(1000)
    df.write.format("delta").save(delta_path)
    print("✅ Version 0 created.")

    print("📝 Simulating an update (Version 1)...")
    spark.sql(f"UPDATE delta.`{delta_path}` SET ratings = ratings + 0.1 WHERE ratings < 4.0")
    print("✅ Version 1 created.")

    print("🕰️  Time Travel: Reading Version 0 (Original Data)...")
    df_v0 = spark.read.format("delta").option("versionAsOf", 0).load(delta_path)
    print(f"Version 0 Average Rating: {df_v0.select('ratings').avg().collect()[0][0]:.2f}")

    print("🕰️  Time Travel: Reading Version 1 (Updated Data)...")
    df_v1 = spark.read.format("delta").option("versionAsOf", 1).load(delta_path)
    print(f"Version 1 Average Rating: {df_v1.select('ratings').avg().collect()[0][0]:.2f}")

    spark.stop()
    print("👋 Lakehouse Demo Finished.")

if __name__ == "__main__":
    main()
