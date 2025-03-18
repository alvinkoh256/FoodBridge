import pika
import time

# Default AMQP server configuration
AMQP_HOST = "localhost"  # Change to remote AMQP host if needed
AMQP_PORT = 5672

def connect(host=AMQP_HOST, port=AMQP_PORT, exchange_name=None, exchange_type=None, max_retries=12, retry_interval=5):
    """
    Establish a connection to the AMQP broker and return the connection and channel.
    Retries the connection on failure.

    :param host: Host where RabbitMQ is running (default 'localhost')
    :param port: Port where RabbitMQ is accessible (default 5672)
    :param exchange_name: Exchange to check for existence (optional)
    :param exchange_type: Type of exchange to check for (optional)
    :param max_retries: Max retries for connection (default 12)
    :param retry_interval: Time interval (in seconds) between retries (default 5)
    :return: connection, channel
    """
    retries = 0
    while retries < max_retries:
        retries += 1
        try:
            print(f"Connecting to AMQP broker {host}:{port}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=host,
                    port=port,
                    heartbeat=300,
                    blocked_connection_timeout=300,
                )
            )
            print("Connected to AMQP broker.")
            channel = connection.channel()

            # Check for the existence of the exchange (if specified)
            if exchange_name and exchange_type:
                print(f"Checking existence of exchange: {exchange_name}")
                channel.exchange_declare(
                    exchange=exchange_name,
                    exchange_type=exchange_type,
                    passive=True,  # Passive means it won't create the exchange if it doesn't exist
                )
                print(f"Exchange {exchange_name} exists.")

            return connection, channel

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect: {e}")
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
    
    raise Exception(f"Max {max_retries} retries exceeded...")

def close(connection, channel):
    """
    Close the RabbitMQ connection and channel.

    :param connection: The AMQP connection
    :param channel: The AMQP channel
    """
    channel.close()
    connection.close()
    print("Connection closed.")

def publish_message(exchange_name, routing_key, message, host=AMQP_HOST, port=AMQP_PORT):
    """
    Publishes a message to the specified exchange with a routing key.

    :param exchange_name: The name of the exchange to send the message to
    :param routing_key: The routing key to identify the queue(s)
    :param message: The message to publish
    :param host: Host where RabbitMQ is running (default 'localhost')
    :param port: Port where RabbitMQ is accessible (default 5672)
    """
    connection, channel = connect(host, port)

    # Declare the exchange (if not already declared)
    channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)

    # Publish the message
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=message
    )

    print(f"Message sent to {exchange_name} with routing key {routing_key}: {message}")
    
    close(connection, channel)

def consume_message(queue_name, callback, host=AMQP_HOST, port=AMQP_PORT):
    """
    Starts consuming messages from the specified queue and calls the provided callback function.

    :param queue_name: The name of the queue to consume messages from
    :param callback: The function to call when a message is received
    :param host: Host where RabbitMQ is running (default 'localhost')
    :param port: Port where RabbitMQ is accessible (default 5672)
    """
    connection, channel = connect(host, port)

    # Declare the queue (if not already declared)
    channel.queue_declare(queue=queue_name, durable=True)

    print(f"Consuming from queue: {queue_name}")
    
    # Start consuming messages from the queue
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def is_connection_open(connection):
    """
    Check if the AMQP connection is open.

    :param connection: The AMQP connection
    :return: True if the connection is open, False otherwise
    """
    try:
        connection.process_data_events()
        return True
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        return False
