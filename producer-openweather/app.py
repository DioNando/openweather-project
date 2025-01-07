import os
import json
import time
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
KAFKA_WEATHER_TOPIC = os.getenv('KAFKA_WEATHER_TOPIC', 'weather_topic')
KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:9092')
API_WEATHER_CITY_IDS = os.getenv('API_WEATHER_CITY_IDS', '2538474,1053384,1850147').split(',')
API_WEATHER_URL = os.getenv('API_WEATHER_URL', 'http://api.openweathermap.org/data/2.5/forecast')
API_WEATHER_LANG = os.getenv('API_WEATHER_LANG', 'fr')
API_WEATHER_KEY = os.getenv('API_WEATHER_KEY')
API_WEATHER_UNITS = os.getenv('API_WEATHER_UNITS', 'metric')
FETCH_INTERVAL = 5  # Intervalle de 5 secondes par défaut

# Initialisation des variables
total_cities = len(API_WEATHER_CITY_IDS)
current_index = 0

def fetch_and_publish_weather():
    global current_index

    try:
        # Récupérer l'ID de la ville actuelle
        city_id = API_WEATHER_CITY_IDS[current_index]

        # Appel de l'API
        api_url = f"{API_WEATHER_URL}?id={city_id}&lang={API_WEATHER_LANG}&appid={API_WEATHER_KEY}&units={API_WEATHER_UNITS}"
        response = requests.get(api_url)
        response.raise_for_status()
        weather_data = response.json()

        # Envoi à Kafka
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        producer.send(KAFKA_WEATHER_TOPIC, weather_data)
        producer.flush()

        print(f"Weather data for city ID {city_id} published to Kafka successfully.")

        # Mettre à jour l'index pour la prochaine ville
        current_index = (current_index + 1) % total_cities

    except Exception as e:
        print(f"Error processing city ID {city_id}: {e}")

if __name__ == "__main__":
    print("Starting weather Kafka producer...")

    # Boucle principale
    while True:
        fetch_and_publish_weather()
        time.sleep(FETCH_INTERVAL)
