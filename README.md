```markdown
# Weather Data Pipeline - Kafka Consumer and Email Notifier

## Description

Ce projet est une pipeline de données météo qui utilise Kafka pour consommer des données provenant d'une source externe, les stocke dans une base de données MongoDB et envoie des notifications par email lorsque de nouvelles données sont ajoutées ou mises à jour dans MongoDB. Ce projet inclut également des outils comme MailDev pour l'envoi d'emails locaux, ainsi qu'une interface Streamlit pour visualiser les données en temps réel.

### Fonctionnalités principales :
- **Kafka** : Utilisation de Kafka pour la gestion des flux de données en temps réel.
- **MongoDB** : Stockage des données météo dans une base de données MongoDB.
- **Mailer** : Envoi d'emails conditionnels lorsqu'une nouvelle donnée est ajoutée.
- **Streamlit** : Interface pour visualiser les données météo stockées dans MongoDB avec des graphiques et des tableaux.
- **MailDev** : Serveur SMTP local pour tester l'envoi d'emails.

## Architecture du Projet

Le projet utilise `Docker` pour exécuter plusieurs services interconnectés, qui sont :

- **Kafka** et **Zookeeper** : Kafka est utilisé pour publier et consommer les données météo.
- **MongoDB** : Base de données NoSQL pour stocker les données météo.
- **MailDev** : Utilisé comme serveur SMTP pour tester l'envoi d'emails.
- **Streamlit** : Interface utilisateur pour afficher les données météo en temps réel.
- **Mailer Service** : Envoie des emails de notification lorsqu'une nouvelle donnée est ajoutée dans MongoDB.

## Prérequis

Avant de commencer, vous devez avoir installé les éléments suivants :

- [Docker](https://www.docker.com/products/docker-desktop)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Une clé API de [OpenWeather](https://openweathermap.org/api) (si vous utilisez un service météo externe).

## Configuration

### Variables d'environnement

Dans le fichier `.env`, définissez les variables nécessaires pour que les services fonctionnent correctement :

```env
MONGO_URI=mongodb://root:example@mongodb:27017/?authSource=admin
MONGO_DB_WEATHER=weather_db
MONGO_COLLECTION_WEATHER=forecast_data

KAFKA_WEATHER_TOPIC=weather_data
KAFKA_SERVER=kafka:9092

API_WEATHER_URL=http://api.openweathermap.org/data/2.5/forecast?
API_WEATHER_KEY=your_openweather_api_key
API_WEATHER_CITY_IDS=city_ids
API_WEATHER_LANG=fr
API_WEATHER_UNITS=metric
FETCH_INTERVAL=10  # Intervalle de récupération des données en secondes
```

### Démarrer l'application

1. Clonez ce repository sur votre machine locale :
   ```bash
   git clone https://github.com/DioNando/openweather-project
   cd openweather-project
   ```

2. Assurez-vous que Docker et Docker Compose sont installés sur votre machine.

3. Construisez et démarrez les services avec Docker Compose :
   ```bash
   docker-compose up --build
   ```

4. Accédez à l'interface Streamlit :
   - Ouvrez votre navigateur et allez sur [http://localhost:8501](http://localhost:8501) pour voir les données météo sous forme de graphiques.

5. L'interface MailDev est accessible à l'adresse [http://localhost:1080](http://localhost:1080), où vous pouvez voir les emails envoyés.

### Services disponibles

- **Airflow** : Port 8080 (utilisé pour la gestion des messages Kafka en tant que producer et scheduler).
- **Kafka** : Port 9092 (utilisé pour la gestion des messages Kafka).
- **MongoDB** : Port 27017 (base de données pour stocker les données météo).
- **MailDev** : Port 1080 (interface web pour tester les emails) et Port 1025 (serveur SMTP).
- **Streamlit** : Port 8501 (interface utilisateur pour visualiser les données météo).

## Processus d'envoi d'email

Le service **Mailer** envoie des emails conditionnellement, chaque fois qu'une nouvelle donnée météo est ajoutée à MongoDB. Ce processus fonctionne comme suit :
1. Le **Kafka Producer** publie des données météo récupérées depuis l'API OpenWeather.
2. Le **Kafka Consumer** consomme ces données et les enregistre dans MongoDB.
3. Le service **Mailer** vérifie régulièrement si de nouvelles données ont été ajoutées à MongoDB.
4. Si de nouvelles données sont détectées, un email est envoyé à l'adresse spécifiée dans la configuration.

## Diagramme d'architecture

Voici une représentation simplifiée de l'architecture du projet :

```
+--------------------+       +-----------------+       +-------------------+
| OpenWeather API    | --->  | Kafka Producer  | --->  | Kafka             |
|                    |       |                 |       |                   |
+--------------------+       +-----------------+       +-------------------+
                                          |                   
                                          v
                                 +---------------------+
                                 | Kafka Consumer      |
                                 | (MongoDB Insert)     |
                                 +---------------------+
                                          |
                                          v
                                 +---------------------+
                                 | MongoDB             |
                                 | (weatherData)       |
                                 +---------------------+
                                          |
                                          v
                                 +---------------------+
                                 | Mailer (Email Send) |
                                 +---------------------+
                                          |
                                          v
                                 +---------------------+
                                 | MailDev (SMTP)      |
                                 +---------------------+
```

## Test et Débogage

- Vous pouvez tester l'envoi d'emails via MailDev, accessible à l'URL [http://localhost:1080](http://localhost:1080).
- Pour tester le service Kafka, vous pouvez publier des messages manuellement dans Kafka et vérifier s'ils sont bien consommés et stockés dans MongoDB.

## Améliorations possibles

- Ajout d'une interface pour la gestion dynamique des villes à surveiller (ajouter/supprimer des villes depuis l'interface Streamlit).
- Intégration de plus de sources de données météo ou d'autres types de services en temps réel.
- Ajouter un système d'alertes basé sur des seuils de données (par exemple, alertes sur une température extrême).

## Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer ce projet, n'hésitez pas à ouvrir un "Pull Request". Vous pouvez également signaler des bugs ou proposer des améliorations via les issues.

## Licence

Ce projet est sous licence [MIT](https://opensource.org/licenses/MIT).

---
