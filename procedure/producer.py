import pika
import json

message = {
    "type": "new_user",
    "user_id": 123,
    "email": "user@example.com",
    "is_active": True
}

#connet to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',port='5672'))
channel = connection.channel()

#Declare Queue
channel.queue_declare(queue='tasks')

#publish JSON message
channel.basic_publish(
    exchange='',
    routing_key='tasks',
    body=json.dumps(message)
)

print(f" [x] Sent {message}")
connection.close()