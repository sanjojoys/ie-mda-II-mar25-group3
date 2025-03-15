from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType

# Define your schema
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("user_id", StringType()) \
    .add("age", IntegerType()) \
    .add("gender", StringType()) \
    .add("height", IntegerType()) \
    .add("interests", StringType()) \
    .add("looking_for", StringType()) \
    .add("children", StringType()) \
    .add("education_level", StringType()) \
    .add("occupation", StringType()) \
    .add("swiping_history", StringType()) \
    .add("frequency_of_usage", StringType()) \
    .add("state", StringType())

spark = SparkSession.builder.appName("SparkKafkaStreaming").getOrCreate()

# Kafka source
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9093") \
    .option("subscribe", "first_topic") \
    .option("startingOffsets", "earliest") \
    .load()

json_df = df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# Write the stream output to HDFS
query = json_df.writeStream \
    .format("csv") \
    .option("path", "hdfs://hdfs-namenode:8020/kafka_data")  \
    .option("checkpointLocation", "hdfs://hdfs-namenode:8020/kafka_checkpoint") \
    .outputMode("append") \
    .start()

query.awaitTermination()