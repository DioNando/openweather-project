import smtplib
import time

def send_email():
    sender_email = "no-reply@example.com"
    receiver_email = "test@example.com"
    message = "Subject: Kafka Consumer Update\n\nNew data has been added to MongoDB."

    # Connect to MailDev SMTP server
    with smtplib.SMTP("maildev", 1025) as server:  # Utilise MailDev comme serveur SMTP
        server.sendmail(sender_email, receiver_email, message)
        print("Email sent!")

if __name__ == "__main__":
    while True:
        send_email()
        time.sleep(600)  # Envoie un mail toutes les 10 minutes
