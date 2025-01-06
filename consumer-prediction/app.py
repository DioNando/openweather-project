from kafka import KafkaConsumer, KafkaProducer
import json
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Kafka Configuration
KAFKA_SERVER = 'kafka:9092'
KAFKA_WEATHER_TOPIC = os.getenv('KAFKA_WEATHER_TOPIC', 'weather_topic')
KAFKA_ALERT_TOPIC = os.getenv('KAFKA_ALERT_TOPIC', 'alert_topic')

# API Configuration
API_WEATHER_URL = os.getenv('API_WEATHER_URL')
API_WEATHER_ENDPOINT = os.getenv("API_WEATHER_ENDPOINT")
API_WEATHER_KEY = os.getenv('API_WEATHER_KEY')
API_WEATHER_LANG = os.getenv('API_WEATHER_LANG')
API_WEATHER_UNITS = os.getenv('API_WEATHER_UNITS')

# Initialiser Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

# Initialiser le consommateur Kafka
consumer = KafkaConsumer(
    KAFKA_WEATHER_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

def process_message(data):
    """Traite un message du consumer Kafka pour prévoir les conditions climatiques futures."""
    try:
        # Extraire les données nécessaires
        city_id = data.get("city", {}).get("id")
        city = data.get("city", {}).get("name")
        country = data.get("city", {}).get("country"),
        lat = data.get("city", {}).get("coord", {}).get("lat")
        lon = data.get("city", {}).get("coord", {}).get("lon")
        temperature = data.get("list", [{}])[0].get("main", {}).get("temp")
        humidity = data.get("list", [{}])[0].get("main", {}).get("humidity")
        weather_description = data.get("list", [{}])[0].get("weather", [{}])[0].get("description")
        wind_speed = data.get("list", [{}])[0].get("wind", {}).get("speed")
        pressure = data.get("list", [{}])[0].get("main", {}).get("pressure")

        # Vérifier la validité des données
        if lat is None or lon is None:
            print("Latitude ou longitude manquante dans le message.")
            return

        # Construire l'URL pour l'API de prévisions météo
        # api_url = (
        #     f"{API_WEATHER_URL}/{API_WEATHER_ENDPOINT}?lat={lat}&lon={lon}&appid={API_WEATHER_KEY}"
        # )
        api_url = f"{API_WEATHER_URL}?id={city_id}&lang={API_WEATHER_LANG}&appid={API_WEATHER_KEY}&units={API_WEATHER_UNITS}"

        print(f"API URL: {api_url}")

        # Appel API pour obtenir les prévisions
        response = requests.get(api_url)
        response.raise_for_status()
        forecast_data = response.json()

        # Analyser les prévisions
        future_temperatures = [forecast['main']['temp'] for forecast in forecast_data['list'][:3]]  # 3 prochaines heures
        max_temperature = max(future_temperatures)

        # Détecter une alerte
        alert_message = None
        if max_temperature > 35:  # Exemple: Température supérieure à 35°C
            alert_message = f"Alert: Heatwave expected in {city}, {country}. Temperature reaching {max_temperature}°C."

        if alert_message:
            alert_data = {
                "city": city,
                "country": country,
                "alert_message": alert_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            producer.send(KAFKA_ALERT_TOPIC, alert_data)
            producer.flush()
            print(f"Alert sent for {city}: {alert_message}")

        # Publier les données de prévisions
        prediction_data = {
            "city_id": city_id,
            "city": city,
            "country": country,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "pressure": pressure,
            "weather_description": weather_description,
            "forecast": future_temperatures,
            "timestamp": datetime.utcnow().isoformat()
        }

        producer.send(KAFKA_WEATHER_TOPIC, prediction_data)
        producer.flush()
        print(f"Weather forecast for {city}, {country} published successfully.")

    except Exception as e:
        print(f"Error processing message: {e}")

# def consume_kafka_messages():
#     """Consomme les messages Kafka et les traite."""
#     consumer = KafkaConsumer(
#         KAFKA_WEATHER_TOPIC,
#         bootstrap_servers=KAFKA_SERVER,
#         auto_offset_reset="earliest",
#         enable_auto_commit=True,
#         value_deserializer=lambda v: json.loads(v.decode('utf-8')),
#         consumer_timeout_ms=1000,
#     )

#     print(f"Consuming messages from topic: {KAFKA_WEATHER_TOPIC}")
#     for message in consumer:
#         process_message(message)

# if __name__ == "__main__":
#     print("Starting Kafka Weather Service...")
#     consume_kafka_messages()

if __name__ == '__main__':
    print("Démarrage du consommateur Kafka...")
    try:
        for message in consumer:
            print("Message reçu de Kafka.")
            process_message(message.value)
    except KeyboardInterrupt:
        print("Consommateur Kafka arrêté.")
