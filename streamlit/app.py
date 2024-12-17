import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
import time

# Configuration
MONGO_URI = os.getenv('MONGO_URI')  # Connexion MongoDB
MONGO_DB = os.getenv('MONGO_DB')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION')

# Initialiser le client MongoDB
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

def convert_timestamp_to_time(timestamp):
    """Convertir un timestamp en format hh:mm."""
    return datetime.utcfromtimestamp(timestamp).strftime('%H:%M')

def fetch_data():
    """Récupérer les données depuis MongoDB."""
    try:
        data = list(mongo_collection.find({}, {'_id': 0}).sort("_id", -1))
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

# Interface Streamlit
st.title("Visualisation des données météo")

# Ajouter une option pour l'auto-refresh
auto_refresh = st.checkbox("Activer l'actualisation automatique toutes les 10 secondes", value=False)

# Charger les données
data = fetch_data()
df = create_dataframe(data)

# Afficher les données
if not df.empty:
    st.subheader("Tableau des données")
    st.dataframe(df)

# Afficher les graphiques
plot_data(df)

# Boucle pour actualisation automatique
if auto_refresh:
    # Sleep pendant 10 secondes avant de relancer
    time.sleep(10)
    st.rerun()
