import random
import json
import time
from datetime import datetime, timedelta
from faker import Faker
from confluent_kafka import Producer

# Kafka Configuration
KAFKA_BROKER = "localhost:9092"   # or "kafka:9092" if in Docker
KAFKA_TOPIC = "first_topic"

# Initialize Faker
fake = Faker()

# Sample categorical data with weights for realistic distribution
genders = ["Male", "Female"]
gender_weights = [0.6, 0.4]

interests = ["Sports", "Reading", "Movies"]
interest_weights = [0.4, 0.3, 0.3]

looking_for = ["Casual Dating", "Marriage"]
looking_for_weights = [0.7, 0.3]

children_status = ["Yes", "No"]
children_status_weights = [0.2, 0.8]

education_levels = ["High School", "Bachelor's", "Master's", "Ph.D."]
education_level_weights = [0.3, 0.4, 0.2, 0.1]

occupations = ["Doctor", "Engineer", "Artist", "Teacher", "Lawyer", "Entrepreneur"]
occupation_weights = [0.1, 0.3, 0.1, 0.2, 0.1, 0.2]

usage_frequencies = ["Daily", "Weekly", "Monthly"]
usage_frequency_weights = [0.5, 0.3, 0.2]

# US States list (short sample)
us_states = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
    "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
    "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
    "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey",
    "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma",
    "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming"
]

# Initialize Kafka Producer
producer = Producer({"bootstrap.servers": KAFKA_BROKER})

def generate_random_timestamp(start_date, end_date):
    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    random_timestamp = start_date + timedelta(seconds=random_seconds)
    return random_timestamp.strftime("%Y-%m-%d %H:%M:%S")

def generate_user_event():
    start_date = datetime(2025, 1, 1)
    end_date = datetime.now()
    return {
        "timestamp": generate_random_timestamp(start_date, end_date),
        "user_id": fake.uuid4(),
        "age": random.randint(18, 35),
        "gender": random.choices(genders, weights=gender_weights, k=1)[0],
        "height": round(random.uniform(4.9, 6.5), 2),
        "interests": random.choices(interests, weights=interest_weights, k=random.randint(1, 3)),
        "looking_for": random.choices(looking_for, weights=looking_for_weights, k=1)[0],
        "children": random.choices(children_status, weights=children_status_weights, k=1)[0],
        "education_level": random.choices(education_levels, weights=education_level_weights, k=1)[0],
        "occupation": random.choices(occupations, weights=occupation_weights, k=1)[0],
        "swiping_history": random.randint(0, 500),
        "frequency_of_usage": random.choices(usage_frequencies, weights=usage_frequency_weights, k=1)[0],
        "state": random.choice(us_states)
    }

def send_to_kafka(num_events=200):
    for _ in range(num_events):
        event = generate_user_event()
        producer.produce(KAFKA_TOPIC, value=json.dumps(event))
        producer.flush()
        print(f"Sent: {event}")
        time.sleep(random.uniform(0.3, 0.5))

if __name__ == "__main__":
    send_to_kafka(2000)  # send 2000 events