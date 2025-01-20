import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv
import time
import plotly.express as px
import seaborn as sns
from windrose import WindroseAxes

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
        data = list(mongo_collection.find({}, {'_id': 0}).sort("_id", -1).limit(2500))
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

# Charger les données
data = fetch_data()
df = create_dataframe(data)

# Interface Streamlit avec pages
st.title("Visualisation des données météo 🌤️")
st.markdown(
    "Bienvenue dans l'application de visualisation des données météo. Naviguez via le menu à gauche pour explorer différentes analyses."
)

# Ajouter une barre latérale pour la navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Tableau des données", "Graphiques des températures", "Autres graphiques", "Carte"]
)

# Page 1 : Tableau des données
if page == "Tableau des données":
    st.header("📋 Tableau des données météo")
    st.markdown("Cette section affiche un tableau interactif des données collectées.")

    if not df.empty:
        # Filtre multiselect pour les villes
        selected_cities = st.multiselect(
            "Filtrer par ville", 
            options=df['ville'].unique(),
            default=df['ville'].unique(),
            key="filter_cities"  # Utiliser une clé unique pour assurer un bon fonctionnement
        )

        # Filtrer les données
        filtered_df = df[df['ville'].isin(selected_cities)]

        # Option pour l'auto-refresh
        auto_refresh = st.checkbox(
            f"Activer l'actualisation automatique toutes les {FETCH_INTERVAL} secondes", 
            value=False
        )

        # Afficher le tableau filtré
        if not filtered_df.empty:
            st.write(f"Nombre de lignes affichées : {len(filtered_df)}")
            st.dataframe(filtered_df)
        else:
            st.warning("Aucune donnée à afficher pour les villes sélectionnées.")
    else:
        st.warning("Aucune donnée disponible.")

    # Gestion de l'auto-refresh
    if auto_refresh:
        time.sleep(FETCH_INTERVAL)
        st.rerun()

# Page 2 : Graphiques des températures
elif page == "Graphiques des températures":
    st.header("🌡️ Graphiques des températures")
    st.markdown("Analysez les températures moyennes, ressenties et leur évolution.")

    if not df.empty:
        # Graphique des températures par ville
        fig, ax = plt.subplots()
        ax.bar(df['ville'], df['température'], label='Température', color='skyblue')
        ax.set_xlabel("Ville")
        ax.set_ylabel("Température (°C)")
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Températures minimale et maximale par ville
        fig, ax = plt.subplots()
        df.groupby('ville')[['température_minimale', 'température_maximale']].mean().plot(kind='bar', ax=ax, color=['blue', 'red'])
        ax.set_xlabel("Ville")
        ax.set_ylabel("Température (°C)")
        ax.legend(["Température minimale", "Température maximale"])
        st.pyplot(fig)

        # Comparaison des températures ressenties et réelles
        st.subheader("Comparaison des températures ressenties et réelles par ville")
        fig, ax = plt.subplots()
        df.groupby('ville')[['température', 'température_ressentie']].mean().plot(kind='bar', ax=ax, color=['orange', 'cyan'])
        ax.set_xlabel("Ville")
        ax.set_ylabel("Température (°C)")
        ax.legend(["Température réelle", "Température ressentie"])
        st.pyplot(fig)

        # Évolution des températures
        selected_city = st.selectbox("Sélectionnez une ville pour l'évolution des températures", df['ville'].unique())
        city_data = df[df['ville'] == selected_city]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(city_data['heure'], city_data['température'], label='Température', color='blue')
        ax.fill_between(
            city_data['heure'], 
            city_data['température_minimale'], 
            city_data['température_maximale'], 
            color='skyblue', alpha=0.3, label='Plage de température'
        )
        ax.set_title(f"Évolution des températures à {selected_city}")
        ax.set_xlabel('Heure')
        ax.set_ylabel('Température (°C)')
        ax.legend()
        st.pyplot(fig)
    else:
        st.warning("Aucune donnée disponible.")

# Page 3 : Autres graphiques
elif page == "Autres graphiques":
    st.header("📊 Autres graphiques")
    st.markdown("Explorez des visualisations supplémentaires des données météo.")

    if not df.empty:
        # Histogramme de l'humidité
        st.subheader("Répartition de l'humidité")
        fig, ax = plt.subplots()
        ax.hist(df['humidité'], bins=10, color='lightgreen', edgecolor='black')
        ax.set_xlabel("Humidité (%)")
        ax.set_ylabel("Nombre d'occurrences")
        ax.set_title("Distribution de l'humidité")
        st.pyplot(fig)

        # Couverture nuageuse moyenne par ville
        st.subheader("Couverture nuageuse moyenne par ville")
        fig, ax = plt.subplots()
        df.groupby('ville')['couverture_nuageuse'].mean().plot(kind='bar', ax=ax, color='gray')
        ax.set_xlabel("Ville")
        ax.set_ylabel("Couverture nuageuse (%)")
        st.pyplot(fig)

        # Répartition des descriptions météo
        weather_counts = df['description_météo'].value_counts()
        fig, ax = plt.subplots()
        ax.bar(weather_counts.index, weather_counts.values, color='orange')
        ax.set_xlabel("Description météo")
        ax.set_ylabel("Nombre d'occurrences")
        ax.set_xticklabels(weather_counts.index, rotation=45, ha='right')
        st.pyplot(fig)

        # Répartition des types de météo
        st.subheader("Répartition des types de météo")
        fig, ax = plt.subplots()
        weather_counts = df['description_météo'].value_counts()
        ax.pie(weather_counts, labels=weather_counts.index, autopct='%1.1f%%', colors=plt.cm.tab20.colors)
        ax.set_title("Types de météo")
        st.pyplot(fig)

        # Vitesse moyenne du vent par ville
        st.subheader("Vitesse moyenne du vent par ville")
        fig, ax = plt.subplots()
        df.groupby('ville')['vitesse_vent'].mean().plot(kind='bar', ax=ax, color='purple')
        ax.set_xlabel("Ville")
        ax.set_ylabel("Vitesse du vent (m/s)")
        st.pyplot(fig)
    
        # Distribution des vitesses de vent
        st.subheader("Distribution des vitesses de vent")
        fig1, ax1 = plt.subplots(figsize=(8, 6))
        sns.histplot(df['vitesse_vent'], bins=30, kde=True, color='blue', ax=ax1)
        ax1.set_title('Distribution des vitesses de vent')
        ax1.set_xlabel('Vitesse du vent (km/h)')
        ax1.set_ylabel('Fréquence')
        st.pyplot(fig1)

        # Rose des vents
        st.subheader("Rose des vents")
        fig2 = plt.figure(figsize=(8, 8))
        ax2 = WindroseAxes.from_ax(fig=fig2)
        ax2.bar(df['direction_vent'], df['vitesse_vent'], normed=True, opening=0.8, edgecolor='white')
        ax2.set_legend(title="Vitesse du vent (km/h)")
        plt.title('Rose des vents')
        st.pyplot(fig2)
    else:
        st.warning("Aucune donnée disponible.")

# Page 4 : Carte
elif page == "Carte":
    st.header("🗺️ Carte interactive")
    st.markdown("Visualisez les données météo sur une carte interactive.")

    if not df.empty:
        fig = px.scatter_geo(
            df, lat='lattitude', lon='longitude', color='température',
            hover_name='ville', size='vitesse_vent', projection='natural earth',
            color_continuous_scale='Viridis', title="Carte des températures"
        )
        st.plotly_chart(fig)
    else:
        st.warning("Aucune donnée disponible.")
