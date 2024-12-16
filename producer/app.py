from flask import Flask, jsonify
from kafka import KafkaProducer
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json

app = Flask(__name__)

# Configuration
KAFKA_TOPIC = 'weather_topic'
KAFKA_SERVER = 'kafka:9092'
API_URL = 'http://api.openweathermap.org/data/2.5/forecast?id=524901&appid=e181f39c92f75588ac5e6cb725896788'
FETCH_INTERVAL = 300  # 5 minutes in seconds

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
