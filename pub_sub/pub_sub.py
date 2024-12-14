import mysql.connector
from datetime import datetime
import os
import json
import requests
import logging
import base64


brevo_api_key = "BREVOS_API_KEY"  # Replace with your actual API key
email_api_url = "https://api.sendinblue.com/v3/smtp/email"  
sender_email = "SENDER_EMAIL"  

conn = mysql.connector.connect(
        host='35.245.73.247',
        user='root',
        password='7SEAS',
    )


def send_email(event, context):
    """Cloud Function triggered by Pub/Sub to send an email using Bravos API"""
    
    pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    logging.info(f"Received message: {pubsub_message}")
    
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, email, user_name FROM authentication_db.user")
    all_users = cursor.fetchall()
    cursor.close()
    for user in all_users:
        user_id, email, username = user
        send_email_via_brevos(email, username, pubsub_message)
      

def send_email_via_brevos(to_email, username, body):

    subject = f"Hello, {username}!"  
    headers = {
        'api-key': brevos_api_key,
        'Content-Type': 'application/json'
    }
    
    email_body = f"<h1>Hello, {username}!</h1><p>{body}</p>"
    
    payload = {
        "sender": {"name": "Your Service", "email": sender_email},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": email_body
    }

    try:
        response = requests.post(email_api_url, headers=headers, json=payload)
        
        if response.status_code == 201:
            logging.info(f"Email sent to {to_email} successfully!")
        else:
            logging.error(f"Failed to send email to {to_email}: {response.text}")
    
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
