
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType, TimestampType

def main():
    spark = SparkSession.builder \
        .appName("StreamingLab") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
        .getOrCreate()


    schema = StructType() \
        .add("order_id", StringType()) \
        .add("status", StringType()) \
        .add("amount", DoubleType()) \
        .add("timestamp", TimestampType())

    os.makedirs("./streaming_checkpoint", exist_ok=True)
    os.makedirs("./streaming_data", exist_ok=True)

    stream_df = spark.readStream \
        .schema(schema) \
        .json("./streaming_data")

    transformed_stream = stream_df.filter(col("status") == "PLACED") \
        .select("order_id", "amount", "timestamp")

    query = transformed_stream.writeStream \
        .format("console") \
        .outputMode("append") \
        .start()

    print("🚀 Spark Structured Streaming started (Task 21)...")
    print("Watching for new JSON files in ./streaming_data...")
    
    query.stop()
    spark.stop()

if __name__ == "__main__":
    import os
    main()
