from flask import current_app
import smtplib
from email.mime.text import MIMEText

def send_notification(email, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = current_app.config['MAIL_USERNAME']
    msg['To'] = email

    with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        server.send_message(msg) 