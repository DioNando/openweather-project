from kafka import KafkaConsumer, KafkaProducer
import requests
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Kafka Configuration
KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:9092')
KAFKA_WEATHER_TOPIC = os.getenv('KAFKA_WEATHER_TOPIC', 'weather_topic')
KAFKA_HERE_TOPIC = os.getenv('KAFKA_HERE_TOPIC', 'here_topic')

# API Configuration
API_HERE_URL = os.getenv('API_HERE_URL')
API_HERE_ENDPOINT = os.getenv("API_HERE_ENDPOINT")
API_HERE_RADIUS = os.getenv("API_HERE_RADIUS")
API_HERE_LOCATION_REFERENCING = os.getenv("API_HERE_LOCATION_REFERENCING")
API_HERE_KEY = os.getenv('API_HERE_KEY')

# Initialiser Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

def process_message(message):
    """Traite un message du consumer Kafka."""
    try:
        # Charger le message JSON
        weather_data = message.value

        # Extraire latitude et longitude
        city = weather_data.get("city", {}).get("name"),
        lat = weather_data.get("city", {}).get("coord", {}).get("lat")
        lon = weather_data.get("city", {}).get("coord", {}).get("lon")

        if lat is None or lon is None:
            print("Latitude ou longitude manquante dans le message.")
            return

        # Construire l'URL pour l'API HERE
        api_url = (
            f"{API_HERE_URL}/{API_HERE_ENDPOINT}?"
            f"in=circle:{lat},{lon};r={API_HERE_RADIUS}&"
            f"locationReferencing={API_HERE_LOCATION_REFERENCING}&"
            f"apiKey={API_HERE_KEY}"
        )
        print(f"Constructed API URL: {api_url}")

        # Appel API avec les coordonnées
        response = requests.get(api_url)
        response.raise_for_status()
        location_data = response.json()

        # Publier les résultats dans le nouveau topic
        producer.send(KAFKA_HERE_TOPIC, location_data)
        producer.flush()
        print(f"Location {city} for coordinates ({lat}, {lon}) published successfully.")

    except Exception as e:
        print(f"Error processing message: {e}")

def main():
    """Main function to consume and process Kafka messages."""
    consumer = KafkaConsumer(
        KAFKA_WEATHER_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v),
    )

    print(f"Consuming messages from topic: {KAFKA_WEATHER_TOPIC}")
    for message in consumer:
        process_message(message)

if __name__ == "__main__":
    main()
