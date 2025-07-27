from fastapi import FastAPI
from pydantic import BaseModel
import pika
import json

app = FastAPI()

# Message schema
class Message(BaseModel):
    type: str
    user_id: int
    email: str

# RabbitMQ connection setup (reused)
def get_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.exchange_declare(exchange='micro_topic', exchange_type='topic')
    return connection, channel

# Publish endpoint
@app.post("/publish")
def publish_message(message: Message):
    connection, channel = get_channel()

    # Convert to JSON and publish
    channel.basic_publish(
        exchange='micro_topic',
        routing_key=message.type,
        body=json.dumps(message.dict())
    )
    print(f"[x] Sent: {message.dict()}")

    connection.close()
    return {"status": "sent", "message": message.dict()}
