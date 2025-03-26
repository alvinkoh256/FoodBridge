#!/usr/bin/env python3
import os
import amqp_lib
import sys
import json

# Match the configuration of confirmDelivery.py
rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "notificationsS3"
exchange_type = "direct"
queue_name = "reservation"  # This should match your queue name in the setup script
routing_key = "reservation"  # This should match your routing key in confirmDelivery.py

def callback(ch, method, properties, body):
    try:
        message = json.loads(body.decode())
        print("\n------------- RECEIVED MESSAGE -------------")
        print(f"Routing Key: {method.routing_key}")
        print(f"Message Content: {json.dumps(message, indent=2)}")
        print("--------------------------------------------\n")
    except Exception as e:
        print(f"Error processing message: {str(e)}")
    sys.stdout.flush()  # Force print to log

if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - Test Subscriber for confirmDelivery...")
    print(f"Listening on exchange: {exchange_name} with routing key: {routing_key}")
    sys.stdout.flush()  # Flush the startup print

    # Need to create the queue and bind to the exchange with the routing key
    # This is typically done in your setup script but we do it here for testing
    try:
        connection = amqp_lib.connect(
            hostname=rabbit_host,
            port=rabbit_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type
        )[0]  # Get just the connection, not the channel
        
        # We'll create a temporary queue for testing
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )
        connection.close()
        
        print(f"Successfully set up queue: {queue_name}")
        sys.stdout.flush()
    except Exception as e:
        print(f"Error setting up queue: {str(e)}")
        sys.stdout.flush()

    while True:
        try:
            print(f"Starting to consume messages from queue: {queue_name}")
            sys.stdout.flush()
            
            amqp_lib.start_consuming(
                hostname=rabbit_host,
                port=rabbit_port,
                exchange_name=exchange_name,
                exchange_type=exchange_type,
                queue_name=queue_name,
                callback=callback,
            )
        except Exception as exception:
            print(f"Unable to connect to RabbitMQ.\n     {exception=}\n")
            sys.stdout.flush()  # Flush exception logs
            import time