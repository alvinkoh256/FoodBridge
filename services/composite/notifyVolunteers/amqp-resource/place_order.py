from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pika
import sys, os

import amqp_lib
from invokes import invoke_http

app = Flask(__name__)

CORS(app)

order_URL = "http://localhost:5001/order"
shipping_record_URL = "http://localhost:5002/shipping_record"

# RabbitMQ
rabbit_host = "localhost"
rabbit_port = 5672
exchange_name = "order_topic"
exchange_type = "topic"

connection = None 
channel = None

def connectAMQP():
    # Use global variables to reduce number of reconnection to RabbitMQ
    # There are better ways but this suffices for our lab
    global connection
    global channel

    print("  Connecting to AMQP broker...")
    try:
        connection, channel = amqp_lib.connect(
                hostname=rabbit_host,
                port=rabbit_port,
                exchange_name=exchange_name,
                exchange_type=exchange_type,
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
        exit(1) # terminate


@app.route("/place_order", methods=["POST"])
def place_order():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            order = request.get_json()
            print("\nReceived an order in JSON:", order)

            # do the actual work
            # 1. Send order info {cart items}
            result = processPlaceOrder(order)
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print("Error: {}".format(ex_str))

            return jsonify(
                    {
                        "code": 500,
                        "message": "place_order.py internal error:",
                        "exception": ex_str,
                    }
            ), 500

    # if reached here, not a JSON request.
    return jsonify(
        {"code": 400, "message": "Invalid JSON input: " + str(request.get_data())}
    ), 400


def processPlaceOrder(order):
    if connection is None or not amqp_lib.is_connection_open(connection):
        connectAMQP()
    
    # 2. Send the order info {cart items}
    # Invoke the order microservice
    print("  Invoking order microservice...")
    order_result = invoke_http(order_URL, method="POST", json=order)
    print(f"  order_result: { order_result}\n")

    message = json.dumps(order_result)

    # Check the order result; if a failure, send it to the error microservice.
    code = order_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print("  Publish message with routing_key=order.error\n")
        channel.basic_publish(
                exchange=exchange_name,
                routing_key="order.error",
                body=message,
                properties=pika.BasicProperties(delivery_mode=2),
        )
        # make message persistent within the matching queues until it is received by some receiver
        # (the matching queues have to exist and be durable and bound to the exchange)

        # 7. Return error
        return {
            "code": 500,
            "data": {"order_result": order_result},
            "message": "Order creation failure sent for error handling.",
        }

    # 4. Record new order
    # record the activity log anyway
    print("  Publish message with routing_key=order.info\n")
    channel.basic_publish(
        exchange=exchange_name, routing_key="order.info", body=message
    )

    # 5. Send new order to shipping
    # Invoke the shipping record microservice
    print("  Invoking shipping_record microservice...")
    shipping_result = invoke_http(
        shipping_record_URL, method="POST", json=order_result["data"]
    )
    print(f"  shipping_result:{shipping_result}\n")

    # Check the shipping result;
    # if a failure, send it to the error microservice.
    code = shipping_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        print("  Publish message with routing_key=shipping.error\n")
        message = json.dumps(shipping_result)
        channel.basic_publish(
                exchange=exchange_name,
                routing_key="shipping.error",
                body=message,
                properties=pika.BasicProperties(delivery_mode=2),
        )

        # 7. Return error
        return {
            "code": 400,
            "data": {"order_result": order_result, "shipping_result": shipping_result},
            "message": "Simulated shipping record error sent for error handling.",
        }

    # 7. Return created order, shipping record
    return {
        "code": 201,
        "data": {"order_result": order_result, "shipping_result": shipping_result},
    }


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    connectAMQP()
    app.run(host="0.0.0.0", port=5100, debug=True)
