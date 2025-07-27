import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#declare exchange and a unique queue
channel.exchange_declare(exchange='micro_topic',exchange_type='topic',)
result = channel.queue_declare('',exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='micro_topic',queue=queue_name,routing_key='user.*')

def callback(ch,method,properties,body):
    data = json.loads(body.decode())
    print(f" [x] Received {data}")

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
print('[*] Waiting for user related messages...')
channel.start_consuming()
