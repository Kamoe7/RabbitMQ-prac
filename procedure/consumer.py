import pika
import json

#connect to rabbitMq
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',port=5672))
channel= connection.channel()

#Declare queued
channel.queue_declare(queue='tasks')

#callback to process messages
def callback(ch, method, properties, body):
    data = json.loads(body.decode())
    print(f" [x] Received JSON message: {data}")

    #you can route based on  message type
    if data['type'] == "new_user":
        print(f"-> creating user Id {data['user_id']} with email {data['email']}")

channel.basic_consume(queue='tasks',
                      on_message_callback=callback,
                      auto_ack=True
                      )

print(' [*] Waiting for JSON messages. To exit press')
channel.start_consuming()