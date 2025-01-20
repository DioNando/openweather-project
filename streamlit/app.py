import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import plotly.express as px

# Charger les variables d'environnement
load_dotenv()

# Configuration
MONGO_URI = os.getenv('MONGO_URI')  # Connexion MongoDB
MONGO_DB_WEATHER = os.getenv('MONGO_DB_WEATHER')
MONGO_COLLECTION_WEATHER = os.getenv('MONGO_COLLECTION_WEATHER')
FETCH_INTERVAL = int(os.getenv('FETCH_INTERVAL', '10'))

# Initialiser le client MongoDB
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_WEATHER]
mongo_collection = mongo_db[MONGO_COLLECTION_WEATHER]

def convert_timestamp_to_time(timestamp):
    """Convertir un timestamp en format hh:mm."""
    return datetime.utcfromtimestamp(timestamp).strftime('%H:%M')

def fetch_data():
    """Récupérer les données depuis MongoDB."""
    try:
        data = list(mongo_collection.find({}, {'_id': 0}).sort("_id", -1).limit(1000))
        return data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return []

def create_dataframe(data):
    """Convertir les données en DataFrame Pandas et formater les timestamps."""
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    
    # Convertir le timestamp en format hh:mm
    if 'horodatage' in df.columns:
        df['heure'] = df['horodatage'].apply(convert_timestamp_to_time)
    
    return df

def plot_data(df):
    """Créer des graphiques basés sur les données."""
    if df.empty:
        st.warning("Aucune donnée à afficher pour les graphiques.")
        return

    # Graphique des températures
    st.subheader("Graphique des températures")
    fig, ax = plt.subplots()
    ax.bar(df['ville'], df['température'], label='Température', color='skyblue')
    ax.set_xlabel("Ville")
    ax.set_ylabel("Température (°C)")
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Températures minimale et maximale par ville
    st.subheader("Températures minimale et maximale par ville")
    fig, ax = plt.subplots()
    df.groupby('ville')[['température_minimale', 'température_maximale']].mean().plot(kind='bar', ax=ax, color=['blue', 'red'])
    ax.set_xlabel("Ville")
    ax.set_ylabel("Température (°C)")
    ax.legend(["Température minimale", "Température maximale"])
    st.pyplot(fig)

    # Évolution de la température dans le temps pour une ville
    selected_city = st.selectbox("Sélectionnez une ville pour voir l'évolution des températures", df['ville'].unique())
    st.subheader(f"Évolution des températures à {selected_city}")
    fig, ax = plt.subplots()
    city_data = df[df['ville'] == selected_city]
    ax.plot(city_data['heure'], city_data['température'], marker='o', label='Température')
    ax.set_xlabel("Heure")
    ax.set_ylabel("Température (°C)")
    ax.legend()
    st.pyplot(fig)

    # Comparaison des températures ressenties et réelles
    st.subheader("Comparaison des températures ressenties et réelles par ville")
    fig, ax = plt.subplots()
    df.groupby('ville')[['température', 'température_ressentie']].mean().plot(kind='bar', ax=ax, color=['orange', 'cyan'])
    ax.set_xlabel("Ville")
    ax.set_ylabel("Température (°C)")
    ax.legend(["Température réelle", "Température ressentie"])
    st.pyplot(fig)

    # Répartition de l'humidité
    st.subheader("Répartition de l'humidité")
    fig, ax = plt.subplots()
    ax.hist(df['humidité'], bins=10, color='lightgreen', edgecolor='black')
    ax.set_xlabel("Humidité (%)")
    ax.set_ylabel("Nombre d'occurrences")
    st.pyplot(fig)

    # Répartition des descriptions météo
    st.subheader("Répartition des descriptions météo")
    weather_counts = df['description_météo'].value_counts()
    fig, ax = plt.subplots()
    ax.bar(weather_counts.index, weather_counts.values, color='orange')
    ax.set_xlabel("Description météo")
    ax.set_ylabel("Nombre d'occurrences")
    ax.set_xticklabels(weather_counts.index, rotation=45, ha='right')
    st.pyplot(fig)

    # Vitesse moyenne du vent par ville
    st.subheader("Vitesse moyenne du vent par ville")
    fig, ax = plt.subplots()
    df.groupby('ville')['vitesse_vent'].mean().plot(kind='bar', ax=ax, color='purple')
    ax.set_xlabel("Ville")
    ax.set_ylabel("Vitesse du vent (m/s)")
    st.pyplot(fig)

    # Couverture nuageuse moyenne par ville
    st.subheader("Couverture nuageuse moyenne par ville")
    fig, ax = plt.subplots()
    df.groupby('ville')['couverture_nuageuse'].mean().plot(kind='bar', ax=ax, color='gray')
    ax.set_xlabel("Ville")
    ax.set_ylabel("Couverture nuageuse (%)")
    st.pyplot(fig)

    # Répartition des types de météo
    st.subheader("Répartition des types de météo")
    fig, ax = plt.subplots()
    weather_counts = df['description_météo'].value_counts()
    ax.pie(weather_counts, labels=weather_counts.index, autopct='%1.1f%%', colors=plt.cm.tab20.colors)
    ax.set_title("Types de météo")
    st.pyplot(fig)

def plot_map(df):
    fig = px.scatter_geo(df, lat='lattitude', lon='longitude', color='température',
                     hover_name='ville', size='vitesse_vent', projection='natural earth',
                     color_continuous_scale='Viridis', title="Carte des températures")
    fig.show()

# Interface Streamlit avec pages
st.title("Visualisation des données météo")

# Ajouter une option pour l'auto-refresh
# auto_refresh = st.checkbox(
#     f"Activer l'actualisation automatique toutes les {FETCH_INTERVAL} secondes", 
#     value=False
# )

# Ajouter une barre latérale pour la navigation
page = st.sidebar.selectbox("Navigation", ["Page 1 : Tableau", "Page 2 : Graphiques", "Page 3 : Map"])

# Charger les données
data = fetch_data()
df = create_dataframe(data)

# # Boucle pour actualisation automatique
# if auto_refresh:
#     # Sleep pendant x secondes avant de relancer
#     time.sleep(FETCH_INTERVAL)
#     st.rerun()

if page == "Page 1 : Tableau":
    st.subheader("Tableau des données")

    # Ajouter une option pour l'auto-refresh
    auto_refresh = st.checkbox(
        f"Activer l'actualisation automatique toutes les {FETCH_INTERVAL} secondes", 
        value=False
    )

    if not df.empty:
        st.dataframe(df)
    else:
        st.warning("Aucune donnée à afficher.")

    # Boucle pour actualisation automatique
    if auto_refresh:
        # Sleep pendant x secondes avant de relancer
        time.sleep(FETCH_INTERVAL)
        st.rerun()

elif page == "Page 2 : Graphiques":
    st.subheader("Graphiques")
    plot_data(df)

elif page == "Page 3 : Map":
    st.subheader("Map")
    plot_map(df)
