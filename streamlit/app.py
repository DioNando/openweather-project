import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt

# Configuration
MONGO_URI = 'mongodb://root:example@mongodb:27017/?authSource=admin'  # Connexion MongoDB
MONGO_DB = 'weather_db'
MONGO_COLLECTION = 'forecast_data'

# Initialiser le client MongoDB
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB]
mongo_collection = mongo_db[MONGO_COLLECTION]

def fetch_data():
    """Récupérer les données depuis MongoDB."""
    try:
        data = list(mongo_collection.find({}, {'_id': 0}))
        return data
    except Exception as e:
        st.error(f"Erreur lors de la récupération des données : {e}")
        return []

def create_dataframe(data):
    """Convertir les données en DataFrame Pandas."""
    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data)

def plot_data(df):
    """Créer des graphiques basés sur les données."""
    if df.empty:
        st.warning("Aucune donnée à afficher pour les graphiques.")
        return

    # Graphique des températures
    st.subheader("Graphique des températures")
    fig, ax = plt.subplots()
    ax.plot(pd.to_datetime(df['timestamp'], unit='s'), df['temperature'], label='Température')
    ax.set_xlabel("Temps")
    ax.set_ylabel("Température (K)")
    ax.legend()
    st.pyplot(fig)

    # Répartition des descriptions météo
    st.subheader("Répartition des descriptions météo")
    weather_counts = df['weather'].value_counts()
    fig, ax = plt.subplots()
    weather_counts.plot(kind='bar', ax=ax)
    ax.set_xlabel("Description météo")
    ax.set_ylabel("Nombre d'occurrences")
    st.pyplot(fig)

# Interface Streamlit
st.title("Visualisation des données météo")

st.write("Cette application affiche les données météo stockées dans MongoDB sous forme de tableau et de graphiques.")

data = fetch_data()
df = create_dataframe(data)

if not df.empty:
    st.subheader("Tableau des données")
    st.dataframe(df)

plot_data(df)