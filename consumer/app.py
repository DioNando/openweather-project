from kafka import KafkaConsumer
from pymongo import MongoClient
import json
import os

# Configuration
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')
KAFKA_SERVER = os.getenv('KAFKA_SERVER')
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB = os.getenv('MONGO_DB')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')

# Initialiser le client MongoDB
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

# Initialiser le consommateur Kafka
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_SERVER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

def process_weather_data(data):
    """Traiter les données météo et les insérer dans MongoDB."""
    try:
        # Exemple : extraction des champs pertinents
        processed_data = {
            "city": data.get("city", {}).get("name"),
            "timestamp": data.get("list", [{}])[0].get("dt"),
            "temperature": data.get("list", [{}])[0].get("main", {}).get("temp"),
            "weather": data.get("list", [{}])[0].get("weather", [{}])[0].get("description")
        }

        # Insérer dans MongoDB
        mongo_collection.insert_one(processed_data)
        print("Données insérées dans MongoDB avec succès.")
    except Exception as e:
        print(f"Erreur lors du traitement ou de l'insertion des données : {e}")

if __name__ == '__main__':
    print("Démarrage du consommateur Kafka...")
    try:
        for message in consumer:
            print("Message reçu de Kafka.")
            process_weather_data(message.value)
    except KeyboardInterrupt:
        print("Consommateur Kafka arrêté.")