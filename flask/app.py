from flask import Flask, jsonify, request, send_file
from services.get_data_and_partial_cleaning import get_data_and_partial_cleaning
from flask_cors import CORS
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from windrose import WindroseAxes
from sklearn.cluster import KMeans
import io
from sklearn.cluster import KMeans
import numpy as np
from sklearn.linear_model import LinearRegression
# Force Matplotlib to use the Agg backend
import matplotlib
from statsmodels.tsa.arima.model import ARIMA
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
    result=result[['temps_formaté', 'température', 'température_maximale', 'température_minimale', 'température_ressentie']]
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

@app.route('/city-clustring')
def city_clustring():
    result = get_data_and_partial_cleaning()
    X = result[['lattitude', 'longitude']].drop_duplicates()
    kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
    X['cluster'] = kmeans.predict(X)
    result = result.merge(X[['lattitude', 'longitude', 'cluster']], on=['lattitude', 'longitude'], how='left')
    result=result[['lattitude', 'longitude', 'cluster']]
    unique_clusters=result["cluster"].unique()
    print(unique_clusters)
    data = {}
    for key, value in result["cluster"].items():
        if value not in data:
            data[value]=[{"x":result['lattitude'][key],"y":result['longitude'][key]}]
        else:
            data[value].append({"x":result['lattitude'][key],"y":result['longitude'][key]})
    return jsonify(data)


@app.route('/temperature-prediction')
def temperature_prediction():
    # Fetch and clean the data
    result = get_data_and_partial_cleaning()
    result = result[result['ville'] == "Rabat"].sort_values('temps_formaté')
    # Ensure 'temps_formaté' is a datetime column
    result['temps_formaté'] = pd.to_datetime(result['temps_formaté'])

    # Compute the 'jour' (day offset) from the minimum temperature date
    result['jour'] = (result['temps_formaté'] - result['temps_formaté'].min()).dt.days

    # Prepare the features (X) and target (y)
    X = result[['jour']]  # Features
    y = result['température']  # Target variable

    # Train the linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Generate future day indices
    jours_futurs = np.array([result['jour'].max() + i for i in range(1, 11)]).reshape(-1, 1)

    # Make predictions for future days
    predictions = model.predict(jours_futurs)

    # Prepare the response data
    data = {
        "temps_formaté": result['temps_formaté'].dt.strftime('%Y-%m-%d').tolist(),  # Convert dates to string
        "temperatures": result['température'].tolist(),
        "jours_future": (pd.to_datetime(result['temps_formaté'].min()) + pd.to_timedelta(jours_futurs.flatten(),
                                                                                         'D')).strftime(
            '%Y-%m-%d').tolist(),  # Convert future dates to string
        "predictions": predictions.tolist()
    }

    return jsonify(data)

def wind_chill(temp, wind_speed):
    return 13.12 + 0.6215 * temp - 11.37 * wind_speed ** 0.16 + 0.3965 * temp * wind_speed ** 0.16

@app.route('/arima-prediction')
def arima_prediction():
    # Fetch and clean the data
    result = get_data_and_partial_cleaning()
    result = result[result['ville'] == "Rabat"].sort_values('temps_formaté')
    result['wind_chill'] = result.apply(lambda row: wind_chill(row['température'], row['vitesse_vent']), axis=1)

    result['temps_formaté'] = pd.to_datetime(result['temps_formaté'])
    result.set_index('temps_formaté', inplace=True)
    temperature_series = result['température']

    train_size = int(len(temperature_series) * 0.8)
    train, test = temperature_series[:train_size], temperature_series[train_size:]

    model = ARIMA(train, order=(5, 1, 0))  # (p, d, q) parameters for ARIMA
    model_fit = model.fit()

    predictions = model_fit.forecast(steps=len(test))

    # Convert Pandas Series to lists
    test_list = test.tolist()
    predictions_list = predictions.tolist()
    test_index_list = test.index.strftime('%d-%m %H:%M').tolist()  # Convert datetime index to string

    data = {
        "test": test_list,
        "predictions": predictions_list,
        "dates": test_index_list
    }

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)