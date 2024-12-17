import smtplib
import time
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def send_email():
    try:
        # Récupérer les informations de connexion à partir des variables d'environnement
        sender_email = os.getenv("SENDER_EMAIL", "no-reply@example.com")
        receiver_email = os.getenv("RECEIVER_EMAIL", "test@example.com")
        smtp_server = os.getenv("SMTP_SERVER", "maildev")
        smtp_port = int(os.getenv("SMTP_PORT", 1025))  # Port par défaut MailDev est 1025
        subject = "Kafka Consumer Update"
        
        # Créer le message HTML avec une date d'envoi
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        body = f"""
        <html>
            <body>
                <h2>New Data Added to MongoDB</h2>
                <p>Data has been successfully added to MongoDB at <strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>.</p>
                <p><a href="http://localhost:8081">View MongoDB</a> to check the data.</p>
            </body>
        </html>
        """
        
        # Attacher le corps HTML au message
        message.attach(MIMEText(body, "html"))
        
        # Connecter au serveur SMTP (MailDev)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Email sent to {receiver_email}!")

    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    while True:
        send_email()
        time.sleep(600)  # Envoie un mail toutes les 10 minutes
