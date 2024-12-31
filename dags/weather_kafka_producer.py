from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from kafka import KafkaProducer
from datetime import datetime, timedelta
import json
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration
KAFKA_WEATHER_TOPIC = os.getenv('KAFKA_WEATHER_TOPIC', 'weather_topic')
KAFKA_SERVER = os.getenv('KAFKA_SERVER', 'localhost:9092')
API_WEATHER_CITY_IDS = os.getenv('API_WEATHER_CITY_IDS', '2538474,1053384,1850147').split(',')
API_WEATHER_URL = os.getenv('API_WEATHER_URL', 'http://api.openweathermap.org/data/2.5/forecast')
API_WEATHER_LANG = os.getenv('API_WEATHER_LANG', 'fr')
API_WEATHER_KEY = os.getenv('API_WEATHER_KEY', 'YOUR_API_WEATHER_KEY')
API_WEATHER_UNITS = os.getenv('API_WEATHER_UNITS', 'metric')
FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', '10'))
EMAIL_RECIPIENT = "your_email@example.com"

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG Definition
with DAG(
    "weather_kafka_producer",
    default_args=default_args,
    description="Pipeline to fetch weather data for cities and send email once the cycle is complete",
    # schedule_interval=timedelta(minutes=30),
    schedule_interval=timedelta(seconds=FETCH_INTERVAL),
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    def fetch_and_publish_weather(**context):
        """Fetch weather data for a city and publish it to Kafka."""
        current_index = Variable.get("current_city_index", default_var=0)
        current_index = int(current_index)

        city_id = API_WEATHER_CITY_IDS[current_index]
        try:
            # Appel API
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

            # Mise à jour de l'index pour la prochaine exécution
            next_index = (current_index + 1) % len(API_WEATHER_CITY_IDS)
            Variable.set("current_city_index", next_index)

            # Sauvegarder le city_id dans XCom
            context['ti'].xcom_push(key='city_id', value=city_id)

            # Vérification du cycle terminé
            if next_index == 0:
                Variable.set("cycle_completed", True)
            else:
                Variable.set("cycle_completed", False)

        except Exception as e:
            print(f"Error processing city ID {city_id}: {e}")
            raise

    def send_email_if_cycle_complete(**context):
        """Send email only if the cycle is complete."""
        is_cycle_complete = Variable.get("cycle_completed", default_var=False)
        if str(is_cycle_complete).lower() == "true":  # Vérifier si le cycle est terminé
            print("Cycle complete. Sending email.")
            email_content = """
            <html>
            <body>
                <h1>Weather Data Pipeline</h1>
                <p>The cycle of fetching weather data for all cities is complete!</p>
                <ul>
                    <li><b>Total Cities Processed:</b> {}</li>
                    <li><b>Kafka Topic:</b> {}</li>
                </ul>
            </body>
            </html>
            """.format(len(API_WEATHER_CITY_IDS), KAFKA_WEATHER_TOPIC)

            # Envoi de l'email
            from airflow.operators.email import EmailOperator
            email_operator = EmailOperator(
                task_id="send_success_email",
                to=EMAIL_RECIPIENT,
                subject="Weather Airflow Producer Pipeline - Cycle Complete",
                html_content=email_content,
            )
            email_operator.execute(context)

    fetch_weather_task = PythonOperator(
        task_id="fetch_data_and_push_to_kafka",
        python_callable=fetch_and_publish_weather,
    )

    email_task = PythonOperator(
        task_id="check_cycle_and_send_email",
        python_callable=send_email_if_cycle_complete,
    )

    # Task Dependencies
    fetch_weather_task >> email_task
