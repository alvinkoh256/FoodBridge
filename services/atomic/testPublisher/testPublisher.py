#!/usr/bin/env python3
import json
import amqp_lib
import time

rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "exampleExchangeName"
exchange_type = "topic"
routing_key = "test.example"

def publish_message():
    message = {"message": "Hello from Publisher!"}
    amqp_lib.publish_message(
        hostname=rabbit_host,
        port=rabbit_port,
        exchange_name=exchange_name,
        exchange_type=exchange_type,
        routing_key=routing_key,
        message=message,
    )

if __name__ == "__main__":
    print("Publisher started. Sending messages every 5 seconds...")
    while True:
        publish_message()
        time.sleep(5)
