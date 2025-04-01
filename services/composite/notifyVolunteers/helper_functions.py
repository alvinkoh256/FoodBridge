from invokes import invoke_http
import os
import amqp_lib
import logging
import json
import pika

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

USER_URL = os.environ.get('ACCOUNT_SERVICE_URL', "https://personal-tdqpornm.outsystemscloud.com/FoodBridge/rest/AccountInfoAPI")
NOTFIY_URL = os.environ.get('NOTIFICATION_URL', "http://localhost:5007")
RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
RABBIT_PORT = int(os.environ.get('RABBIT_PORT', 5672))
RABBIT_PUBLISHER_EXCHANGE = os.environ.get('SCENARIO2_RABBIT_EXCHANGE', 'scenario2NotifyExchange')
EXCHANGE_TYPE = os.environ.get('SCENARIO12_EXCHANGE_TYPE', 'fanout')

def connectAMQP():
    # Use global variables to reduce number of reconnection to RabbitMQ
    # There are better ways but this suffices for our lab
    global connection
    global channel

    print("  Connecting to AMQP broker...")
    try:
        connection, channel = amqp_lib.connect(
                hostname="localhost",
                port=5672,
                exchange_name="scenario2NotifyExchange",
                exchange_type="fanout",
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
        exit(1)

# function to retrieve user phone no.
def get_user_info(user_id):
    try:
        url = f"{USER_URL}/user_id"
        response = invoke_http(
            url,
            'GET',
        )
        return response
    except Exception as e:
        logger.error(f"Error getting user info for user_id {user_id}: {str(e)}")
        return {"error": f"Failed to retrieve user information: {str(e)}"}
    

def process_user_list(user_list):
    lister = []
    # ACTUAL FUNCTION
    for user_id in user_list:
        user_details = get_user_info(user_id)
        user_name = user_details["userName"]
        user_number = user_details["userPhoneNumber"]
        body = {
            "userId":user_id,
            "userName":user_name,
            "userPhoneNumber":user_number,
        }
        lister.append(body)

    dicter = {}
    dicter["userList"] = lister
    return dicter

def sendToQueue(message):
    if connection is None or not amqp_lib.is_connection_open(connection):
        connectAMQP()
    
    # Convert non-string data types (like lists) to JSON strings
    if not isinstance(message, str):
        message = json.dumps(message)
        logger.info(f"Converted message to JSON string: {message}")
    
    # Ensure message is bytes for RabbitMQ
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    channel.basic_publish(exchange=RABBIT_PUBLISHER_EXCHANGE, routing_key="", body=message, properties=pika.BasicProperties(delivery_mode=2))
    logger.info("Message sent to queue successfully")