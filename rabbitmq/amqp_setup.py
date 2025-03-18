#!/usr/bin/env python3

import pika

# Default AMQP server configuration
amqp_host = "localhost"  # Change to remote AMQP host if needed
amqp_port = 5672

# Exchange configurations
topic_exchange_name = "topic_exchange"
fanout_exchange_name = "fanout_exchange"
direct_exchange_name = "direct_exchange"

def create_exchange(channel, exchange_name, exchange_type):
    """
    Creates an exchange if it doesn’t exist.
    """
    print(f"Declaring exchange: {exchange_name} of type {exchange_type}")
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True
    )

def create_queue(channel, exchange_name, queue_name, routing_key):
    """
    Declares a queue and binds it to an exchange using a routing key.
    """
    print(f"Declaring queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)  # durable = survive broker restarts

    print(f"Binding queue: {queue_name} to exchange: {exchange_name} with routing key: {routing_key}")
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )

def setup_amqp():
    # Establish connection to RabbitMQ
    print(f"Connecting to AMQP broker {amqp_host}:{amqp_port}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=amqp_host,
            port=amqp_port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected to AMQP broker.")

    # Open channel
    channel = connection.channel()
    
    # Declare multiple exchanges
    create_exchange(channel, topic_exchange_name, "topic")  # Topic exchange for routing
    create_exchange(channel, fanout_exchange_name, "fanout")  # Fanout exchange for broadcasting
    create_exchange(channel, direct_exchange_name, "direct")  # Direct exchange for exact matching

    # PLEASE READ! Update here with the routing key if your service requires. This code supports the 3 types
    # of exchange. Refer to example below

    # For Topic Exchange: only messages with routing key matching the pattern "order.*" will be sent to the queue
    # create_queue(channel, topic_exchange_name, "topicexample", "example.*")

    # For Fanout Exchange: This will broadcast messages to all queues bound to the exchange
    # create_queue(channel, fanout_exchange_name, "fanoutexample", "")
    
    # For Direct Exchange: This only sends messages to queues with exact routing key match
    # create_queue(channel, direct_exchange_name, "directexample", "example.created")

    # Close the connection
    connection.close()
    print("AMQP setup completed successfully!")

if __name__ == "__main__":
    setup_amqp()
