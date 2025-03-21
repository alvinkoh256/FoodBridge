import os
import amqp_lib
import sys  # <- add this

rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "exampleExchangeName"
exchange_type = "topic"
queue_name = "Example"

def callback(ch, method, properties, body):
    print(f" [x] Received: {body.decode()}")
    sys.stdout.flush()  # <- force print to log

if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - AMQP consumer...")
    sys.stdout.flush()  # <- also flush the startup print

    while True:
        try:
            amqp_lib.start_consuming(
                rabbit_host,
                rabbit_port,
                exchange_name,
                exchange_type,
                queue_name,
                callback,
            )
        except Exception as exception:
            print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
            sys.stdout.flush()  # <- flush exception logs
