from flask import Flask, jsonify, request, send_file
from services.get_data_and_partial_cleaning import get_data_and_partial_cleaning
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from windrose import WindroseAxes
import io
# Force Matplotlib to use the Agg backend
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

CORS(app)

@app.route('/mean-data')
def mean_data():
    result = get_data_and_partial_cleaning().groupby('ville')['température'].mean().sort_values(ascending=False).to_dict()
    villes = list(result.keys())
    temperatures = list(result.values())
    data = {
        "villes": villes,
        "temperatures": temperatures,
    }
    return jsonify(data)

@app.route('/temperature-evolution')
def temperature_evolution():
    result = get_data_and_partial_cleaning()
    ville_cible = 'Rabat'  # Remplacez par une ville de votre fichier
    result = result[result['ville'] == ville_cible].sort_values('temps_formaté')  # Trier par 'temps_formaté'
    result=result[['temps_formaté', 'température', 'température_maximale']]
    result['temps_formaté'] = result['temps_formaté'].dt.strftime('%d.%m %H:%M')
    return jsonify(result.to_dict())

@app.route('/wind-speed')
def wind_speed():
    ville_cible = request.args.get('city')
    result = get_data_and_partial_cleaning()
    villes = result['ville'].unique().tolist()
    result = result[result['ville'] == ville_cible].sort_values('temps_formaté')  # Trier par 'temps_formaté'
    result=result[['temps_formaté', 'vitesse_vent']]
    result['temps_formaté'] = result['temps_formaté'].dt.strftime('%d.%m %H:%M')
    result=result.to_dict()
    result['villes']=villes
    return jsonify(result)

@app.route('/wind-direction')
def wind_direction():
    try:
        # Fetch and preprocess data
        result = get_data_and_partial_cleaning()

        # Create the chart
        fig = plt.figure(figsize=(8, 8))
        fig.patch.set_facecolor('#f9fafb')  # Light gray background (bg-gray-50)

        # Create the wind rose chart
        ax = WindroseAxes.from_ax(fig=fig)
        ax.bar(result['direction_vent'], result['vitesse_vent'], normed=True, opening=0.8, edgecolor='white')
        ax.set_facecolor('#f9fafb')  # Light gray background (matches the figure background)
        ax.set_legend()

        # Add a title
        plt.title('Rose des vents', color='black', fontsize=16)

        # Save the chart to a binary stream
        img = io.BytesIO()
        plt.savefig(img, format='png', facecolor=fig.get_facecolor())  # Save figure with background
        img.seek(0)  # Reset the stream position to the beginning
        plt.close(fig)  # Close the figure to free resources

        # Return the image as a response
        return send_file(img, mimetype='image/png')
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/anomaly-counting')
def anomaly_counting():
    ville_cible = request.args.get('city')
    result = get_data_and_partial_cleaning()
    villes = result['ville'].unique().tolist()
    result = result[result['ville'] == ville_cible].sort_values('temps_formaté')  # Trier par 'temps_formaté'
    # Calculer la température moyenne pour chaque mois
    result['mois'] = result['temps_formaté'].dt.strftime('%d.%m %H:%M')
    moyenne_temp_mensuelle = result.groupby('mois')['température'].mean()

    # Calculer l'écart par rapport à la moyenne
    result['anomalie_temp'] = result['température'] - result['mois'].map(moyenne_temp_mensuelle)
    result=result[['anomalie_temp','mois']]
    result=result.to_dict()
    result['villes']=villes
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)