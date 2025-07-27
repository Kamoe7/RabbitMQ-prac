import pika
import json


message = {
    "type": "user.signup",
    "user_id": 42,
    "email": "test@example.com"
}

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='micro_topic',exchange_type='topic')

channel.basic_publish(
    exchange='micro_topic',
    routing_key=message['type'],
    body=json.dumps(message)
)

print(f" [x] Sent {message}")
connection.close()