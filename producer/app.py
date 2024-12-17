from flask import Flask, jsonify
from kafka import KafkaProducer
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Configuration
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_SERVER = os.getenv('KAFKA_SERVER')
API_URL = os.getenv('API_URL')
FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', '10'))

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_and_publish_weather():
    """Fetch weather data from the API and publish it to Kafka."""
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        weather_data = response.json()

        # Publish to Kafka
        producer.send(KAFKA_TOPIC, weather_data)
        print("Weather data published to Kafka successfully.")
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except Exception as e:
        print(f"Error publishing to Kafka: {e}")

# Scheduler to run fetch_and_publish_weather every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_publish_weather, 'interval', seconds=FETCH_INTERVAL)
scheduler.start()

@app.route('/')
def index():
    return jsonify({"message": "Kafka producer is running and fetching data every 5 minutes."})

if __name__ == '__main__':
    try:
        # Start Flask app
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped and application exiting.")
