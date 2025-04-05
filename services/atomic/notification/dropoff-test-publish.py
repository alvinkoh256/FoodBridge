#!/usr/bin/env python3
import json
import amqp_lib
import time
import os

# rabbit_host = "rabbitmq"
# rabbit_port = 5672
# exchange_name = "exampleExchangeName"
# exchange_type = "topic"
# routing_key = "test.example"

RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
RABBIT_PORT = int(os.environ.get('RABBIT_PORT', 5672))
RABBIT_SUBSCRIBER_EXCHANGE = os.environ.get('SCENARIO12_RABBIT_EXCHANGE', 'scenario12Exchange')
RABBIT_SUBSCRIBER_EXCHANGE_TYPE = os.environ.get('SCENARIO12_EXCHANGE_TYPE', 'fanout')
RABBIT_SUBSCRIBER_QUEUE = "scenario12"

def publish_message():
    message = {"volunteerName": "Bob",
               "volunteerMobile": "+6590603108"}
    amqp_lib.publish_message(
        hostname=RABBIT_HOST,
        port=RABBIT_PORT,
        exchange_name="notificationsS3",
        exchange_type="topic",
        routing_key="dropoff",
        message=message,
    )


if __name__ == "__main__":
    print("Publisher started. Sending messages every 5 seconds...")
    # while True:
    publish_message()
        # time.sleep(5)
