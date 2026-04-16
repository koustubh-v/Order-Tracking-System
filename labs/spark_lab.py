
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg


def main():
    hdfs_模拟_path = "./local_hdfs/data/incoming"
    os.makedirs(hdfs_模拟_path, exist_ok=True)
    print(f"📁 Local HDFS Simulation created at {hdfs_模拟_path}")

    spark = SparkSession.builder \
        .appName("CollegeProjectSparkLab") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    
    print("✨ Spark Session Started (Task 14)")

    df = spark.read.csv("cleaned_combined_products.csv", header=True, inferSchema=True)
    print(f"📊 Loaded {df.count()} rows into Spark DataFrame")

    high_rated = df.filter(col("ratings") >= 4.5)
    print("✅ Transformation: Filtered products with ratings >= 4.5")

    df.createOrReplaceTempView("products")
    print("📉 Spark SQL: Aggregating by category...")
    sql_result.show(10)

    print("⚡ Optimizing Spark Job (Task 17)...")
    df_partitioned = df.repartition(4) # Partitioning
    df_partitioned.cache() # Caching for performance
    print("✅ Data partitioned into 4 slices and cached in memory.")

    spark.stop()
    print("👋 Spark Session Stopped.")

if __name__ == "__main__":
    main()
