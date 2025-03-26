#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ.
"""

import pika

amqp_host = "rabbitmq"
amqp_port = 5672


def create_exchange(hostname, port, exchange_name, exchange_type):
    # Establishes a connection to a RabbitMQ broker and 
    # creates an exchange if it doesn’t exist.
    print(f"Connecting to AMQP broker {hostname}:{port}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname,
            port=port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected")

    print("Open channel")
    channel = connection.channel()

    print(f"Declare exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True
    )

    return channel

def create_queue(channel, exchange_name, queue_name, routing_key):
    # Declares a queue and binds it to an exchange using a routing key
    print(f"Bind to queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)

    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )

# Example exchange & queue for testConsumer.py & testSubscriber.py

# channelExample = create_exchange(
#     hostname=amqp_host,
#     port=amqp_port,
#     exchange_name="exampleExchangeName",
#     exchange_type="topic",
# )

# create_queue(
#     channel=channelExample,
#     exchange_name="exampleExchangeName",
#     queue_name="Example",
#     routing_key="*.example"
# )

scenario12Exchange = create_exchange(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name="scenario12Exchange",
    exchange_type="fanout"
)

create_queue(
    channel=scenario12Exchange,
    exchange_name="scenario12Exchange",
    queue_name="scenario12",
    routing_key=""
)
# This exchange is for confirmDelivery, Hub and Route in Scenario 3.
notificationsExchangeS3 = create_exchange(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name="notificationsS3",
    exchange_type="direct",
)

# confirmDelivery -> Notification
create_queue(
    channel=notificationsExchangeS3,
    exchange_name="notificationsS3",
    queue_name="dropoff",
    routing_key="dropoff"
)

# Hub -> Notification
create_queue(
    channel=notificationsExchangeS3,
    exchange_name="notificationsS3",
    queue_name="broadcastHubs",
    routing_key="broadcastHubs"
)
