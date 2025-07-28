import pika
import json
from pymongo import MongoClient
import os
import time

rabbit_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
mongo_host = os.environ.get("MONGO_HOST", "mongodb")


def connect_rabbitmq():
    retries = 5
    while retries > 0:
        try:
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host=rabbit_host,
                port=5672,
                virtual_host='/',
                credentials=credentials
            )
            connection = pika.BlockingConnection(parameters)
            print("Connected to RabbitMQ!")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"RabbitMQ connection failed: {e}. Retrying in 5 seconds...")
            retries -= 1
            time.sleep(5)
    raise Exception("Failed to connect to RabbitMQ after retries")


def connect_mongodb():
    retries = 10  # Increased retries
    while retries > 0:
        try:
            client = MongoClient(
                f"mongodb://{mongo_host}:27017",
                serverSelectionTimeoutMS=30000,  # Increased to 30 seconds
                connectTimeoutMS=30000,
                socketTimeoutMS=30000
            )
            client.admin.command('ping')  # Test connection
            print("Connected to MongoDB!")
            return client
        except Exception as e:
            print(f"MongoDB connection failed: {e}. Retrying in 10 seconds...")
            retries -= 1
            time.sleep(10)  # Increased delay
    raise Exception("Failed to connect to MongoDB after retries")  # Fixed typo


# Connect to MongoDB and RabbitMQ
mongo_client = connect_mongodb()
db = mongo_client["microservice_db"]
collections = db["messages"]

connection = connect_rabbitmq()
channel = connection.channel()

args = {'x-dead-letter-exchange': 'dlx'}
channel.exchange_declare(exchange='dlx', exchange_type='fanout')
channel.queue_declare(queue='dead_letters')
channel.queue_bind(exchange='dlx', queue='dead_letters')

channel.exchange_declare(exchange='micro_topic', exchange_type='topic')
channel.queue_declare(queue='user_queue', durable=True, arguments=args)
channel.queue_bind(exchange='micro_topic',
                   queue='user_queue', routing_key='user.*')


def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode())
        print(f" [x] Received {data}")
        collections.insert_one(data)
        print(f"Stored in MongoDB: {data}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[!] Error: {e} - sending to DLQ")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


channel.basic_consume(queue='user_queue', on_message_callback=callback)
print("Consumer started and waiting for messages...")
channel.start_consuming()
