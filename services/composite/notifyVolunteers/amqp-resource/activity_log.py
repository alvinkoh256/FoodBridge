#!/usr/bin/env python3
import json
import os
import amqp_lib

rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "order_topic"
exchange_type = "topic"
queue_name = "Activity_Log"


def callback(channel, method, properties, body):
    # required signature for the callback; no return
    try:
        error = json.loads(body)
        print(f"JSON: {error}")
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Message: {body}")
    print()


if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
