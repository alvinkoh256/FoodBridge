"""
Reusable AMQP-related functions

References:
https://pika.readthedocs.io/en/stable/_modules/pika/exceptions.html#ConnectionClosed
"""

import time
import pika
import json

def connect(hostname, port, exchange_name, exchange_type, max_retries=12, retry_interval=5):
    retries = 0
    while retries < max_retries:
        retries += 1
        try:
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

            print(f"Check existence of exchange: {exchange_name}")
            channel.exchange_declare(
                exchange=exchange_name,
                exchange_type=exchange_type,
                durable=True
            )
            return connection, channel

        except pika.exceptions.ChannelClosedByBroker as exception:
            message = f"{exchange_type} exchange {exchange_name} not found."
            connection.close()
            raise Exception(message) from exception

        except pika.exceptions.AMQPConnectionError as exception:
            print(f"Failed to connect: {exception=}")
            print(f"Retrying in {retry_interval} seconds...")
            time.sleep(retry_interval)
    
    raise Exception(f"Max {max_retries} retries exceeded...")

def close(connection, channel):
    channel.close()
    connection.close()

def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True     
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        return False

def start_consuming(hostname, port, exchange_name, exchange_type, queue_name, callback):
    while True:
        try:
            connection, channel = connect(
                hostname=hostname,
                port=port,
                exchange_name=exchange_name,
                exchange_type=exchange_type,
            )

            print(f"Consuming from queue: {queue_name}")
            channel.basic_consume(
                queue=queue_name, on_message_callback=callback, auto_ack=True
            )
            channel.start_consuming()

        except pika.exceptions.ChannelClosedByBroker as exception:
            message = f"Queue {queue_name} not found."
            connection.close()
            raise Exception(message) from exception

        except pika.exceptions.ConnectionClosedByBroker:
            print("Connection closed. Try to reconnect...")
            continue

        except KeyboardInterrupt:
            close(connection, channel)
            break

def publish_message(hostname, port, exchange_name, exchange_type, routing_key, message):
    connection, channel = connect(hostname, port, exchange_name, exchange_type)
    print(f"Publishing message: {message}")
    channel.basic_publish(
        exchange=exchange_name,
        routing_key=routing_key,
        body=json.dumps(message),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    print("Message published.")
    close(connection, channel)
