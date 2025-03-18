#!/usr/bin/env python3

import pika

# Default AMQP server configuration
amqp_host = "localhost"  # Change to the appropriate AMQP host if using a remote server
amqp_port = 5672

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
    channel.queue_declare(queue=queue_name, durable=True)  # durable = survives broker restarts

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
    
    # STEP 1: Declare the Exchange
    # Available exchange types:
    # - "topic" for pattern-based routing (e.g., "order.*")
    # - "direct" for exact routing (e.g., "order.created")
    # - "fanout" for broadcasting (no routing key)
    #
    # Example for a topic exchange:
    # create_exchange(channel, "topic_exchange", "topic")  # Topic exchange for routing

    # add create_exchange() here
    
    # STEP 2: Declare the Queue
    # Choose a queue name and routing key based on your use case:
    #
    # Example for Topic Exchange:
    # create_queue(channel, "topic_exchange", "order_queue", "order.*")
    #
    # Example for Fanout Exchange (no routing key):
    # create_queue(channel, "fanout_exchange", "broadcast_queue", "")
    #
    # Example for Direct Exchange:
    # create_queue(channel, "direct_exchange", "specific_order_queue", "order.created")

    # add create_queue() here


    # STEP 3: Add code in your service to interact with RabbitMQ (refer to README for consuming and publishing messages)

    # Close the connection
    connection.close()
    print("AMQP setup completed successfully!")

if __name__ == "__main__":
    setup_amqp()
