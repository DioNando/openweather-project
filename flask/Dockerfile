# Étape 1 : Utilisation de l'image Python de base
FROM python:3.9-slim

# Étape 2 : Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 3 : Copier les fichiers de l'application dans le conteneur
COPY . /app

# Copier les fichiers nécessaires
COPY services ./
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

# Étape 5 : Exposer le port utilisé par l'application Flask
EXPOSE 5000

# Étape 6 : Définir la commande pour démarrer l'application
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
