import pika
import json

def process(data):
    if data["user_id"] == 42:
        raise Exception('Simulated processing error!')

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

#declare DLX exchange and queue
channel.exchange_declare(exchange='dlx',exchange_type='fanout')
channel.queue_declare(queue='dead_letters')
channel.queue_bind(exchange='dlx',queue='dead_letters')

#declare exchange and a unique queue
args = {'x-dead-letter-exchange' : 'dlx'}
channel.exchange_declare(exchange='micro_topic',exchange_type='topic',)
channel.queue_declare(queue='user_queue',durable=True,arguments=args)
channel.queue_bind(exchange='micro_topic',queue='user_queue',routing_key='user.*')

def callback(ch,method,properties,body):
    try:
        data = json.loads(body.decode())
        print(f" [x] Received {data}")
        process(data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[!] Error: {e} - sending to DLQ")
        ch.basic_nack(delivery_tag= method.delivery_tag,requeue= False)

channel.basic_consume(queue='user_queue', on_message_callback=callback)
print('[*] Waiting for retry an DLQ')
channel.start_consuming()
