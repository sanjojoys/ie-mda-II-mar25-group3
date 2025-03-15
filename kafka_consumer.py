import json
import pandas as pd
import os
from confluent_kafka import Consumer, KafkaError
from hdfs import InsecureClient

# ✅ Kafka Configuration
KAFKA_BROKER = "kafka:9093"  # or "kafka:9093" in Docker
KAFKA_TOPIC = "first_topic"
GROUP_ID = "analytics_group"

# ✅ Initialize Kafka Consumer
consumer = Consumer({
    "bootstrap.servers": KAFKA_BROKER,
    "group.id": GROUP_ID,
    "auto.offset.reset": "earliest"
})
consumer.subscribe([KAFKA_TOPIC])

# ✅ HDFS configuration (update HDFS host/port as needed)
# Read HDFS_URL from environment variable if set, otherwise use localhost
HDFS_URL = os.environ.get("HDFS_URL", "http://localhost:50070")
HDFS_FILE = "/user/hdfs/kafka/kafka_data.csv"
hdfs_client = InsecureClient(HDFS_URL, user="hdfs")

# At startup, remove any existing file in HDFS so every run starts fresh
try:
    hdfs_client.delete(HDFS_FILE, recursive=False)
    print(f"🗑️ Deleted previous HDFS file: {HDFS_FILE}")
except Exception as e:
    print(f"⚠️ Could not delete HDFS file (it might not exist yet): {e}")

# ✅ Define column names
COLUMN_NAMES = [
    "timestamp", "user_id", "age", "gender", "height", "interests",
    "looking_for", "children", "education_level", "occupation",
    "swiping_history", "frequency_of_usage", "state"
]

# ✅ Load existing data if needed (we'll store locally as well)
try:
    data_records = pd.read_csv("data/kafka_data.csv")
    print(f"📂 Loaded existing local data, {len(data_records)} records found.")
except (FileNotFoundError, pd.errors.EmptyDataError):
    data_records = pd.DataFrame(columns=COLUMN_NAMES)
    print("📂 No existing valid local data found, creating new DataFrame.")

def process_event(event_data):
    global data_records

    # Convert event JSON into a DataFrame row
    event_df = pd.DataFrame([event_data])
    data_records = pd.concat([data_records, event_df], ignore_index=True)

    # Convert the updated DataFrame to CSV format
    csv_data = data_records.to_csv(index=False)
    try:
        # Overwrite the HDFS file with the updated CSV data
        with hdfs_client.write(HDFS_FILE, overwrite=True, encoding="utf-8") as writer:
            writer.write(csv_data)
        print(f"✅ Updated HDFS file with {len(data_records)} records.")
    except Exception as e:
        print(f"⚠️ Error writing to HDFS: {e}")

    # Optionally also write locally if you want
    # data_records.to_csv("kafka_data.csv", index=False)

def consume_from_kafka():
    print("🚀 Kafka Consumer Started... Listening for messages")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"⚠️ Consumer Error: {msg.error()}")
                    continue
            try:
                event = json.loads(msg.value().decode("utf-8"))
                process_event(event)
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON Decode Error: {e}")
    except KeyboardInterrupt:
        print("🛑 Stopped by user.")
    finally:
        consumer.close()
        print("✅ Kafka Consumer closed.")

if __name__ == "__main__":
    consume_from_kafka()