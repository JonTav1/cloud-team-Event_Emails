from google.cloud import pubsub_v1
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

project_id = "numeric-ion-437403-q3"
topic_name = "weekly-email-topic"
url = 'http://localhost:8080/api/events'

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)


def get_events():
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        event_array = data
        message = "<p>Here are some upcoming Dining Hall Events:</p>"
        for event in event_array:
            message += f"<div><h3>Location: {event['loc']}</h3><p>Event: {event['event_name']} From {event['start_date']} to {event['end_date']} at {event['time']}</p></div><hr>"
        print("Got messages:")
        print(repr(message))  
        return message

    except requests.exceptions.RequestException as e:
        print(f"Error fetching events: {e}")
        return None


@app.route('/publish', methods=['GET'])
def publish_message(request):
    print("Got events")
    message = "Hello this is puuuub sub"
    #message = get_events()
    if message is None:
        print("Failed to get events")
        return jsonify({"error": "Failed to get events"}), 500

  
    future = publisher.publish(topic_path, message.encode("utf-8"))
    print(f"Message published. Message ID: {future.result()}")

    return jsonify({"message": "Message successfully published", "message_id": future.result()}), 200


if __name__ == "__main__":
    # Run the app on Cloud Run
    app.run(host='0.0.0.0', port=8080)
