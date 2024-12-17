from flask import Flask, jsonify
from kafka import KafkaProducer
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import json
from dotenv import load_dotenv
import os
from itertools import cycle

app = Flask(__name__)

# Configuration
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_SERVER = os.getenv('KAFKA_SERVER')
FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', '10'))

# Liste des IDs des villes
API_CITY_IDS = os.getenv('API_CITY_IDS', '').split(',')
city_cycle = cycle(API_CITY_IDS)  # Crée un itérateur cyclique

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def fetch_and_publish_weather():
    """Fetch weather data for the next city and publish it to Kafka."""
    try:
        city_id = next(city_cycle)  # Obtenir l'ID de la ville suivante
        api_url = os.getenv('API_URL') + f'id={city_id}&lang={os.getenv("API_LANG")}&appid={os.getenv("API_KEY")}&units={os.getenv("API_UNITS")}'
        
        response = requests.get(api_url)
        response.raise_for_status()
        weather_data = response.json()

        # Ajouter des métadonnées sur la ville
        weather_data['city_id'] = city_id

        # Publier dans Kafka
        producer.send(KAFKA_TOPIC, weather_data)
        print(f"Weather data for city ID {city_id} published to Kafka successfully.")
    except requests.RequestException as e:
        print(f"Error fetching data from API for city ID {city_id}: {e}")
    except Exception as e:
        print(f"Error publishing to Kafka: {e}")

# Scheduler to run fetch_and_publish_weather every minute
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_and_publish_weather, 'interval', seconds=FETCH_INTERVAL)
scheduler.start()

@app.route('/')
def index():
    return jsonify({"message": "Kafka producer is running and fetching data every minute."})

if __name__ == '__main__':
    try:
        # Start Flask app
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped and application exiting.")
