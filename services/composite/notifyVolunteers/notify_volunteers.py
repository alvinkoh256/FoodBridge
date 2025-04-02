import os
import json
import amqp_lib
import logging
import helper_functions

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
RABBIT_PORT = int(os.environ.get('RABBIT_PORT', 5672))
RABBIT_SUBSCRIBER_EXCHANGE = os.environ.get('SCENARIO12_RABBIT_EXCHANGE', 'scenario12Exchange')
RABBIT_SUBSCRIBER_EXCHANGE_TYPE = os.environ.get('SCENARIO12_EXCHANGE_TYPE', 'fanout')
RABBIT_SUBSCRIBER_QUEUE = "scenario12"
RABBIT_SENDER_EXCHANGE = "scenario2NotifyExchange"
RABBIT_SENDER_EXCHANGE_TYPE = "fanout"
RABBIT_SENDER_QUEUE = "scenario2Notify"


def callback(channel, method, properties, body):
    # required signature for the callback; no return
    try:
        logger.info(f"Received raw message: {body}")
        
        # Parse the message
        user_list = json.loads(body)
        logger.info(f"Parsed message (JSON): {user_list}")
        
        # Process the data (you can uncomment and use the process_user_list function if needed)
        processed_data = helper_functions.process_user_list(user_list)
        
        # HARDCODED test data for now
        # test_body = {"userList":[
        #     {
        #         "userId":"1111-1111-1111",
        #         "userName":"Yao Hui",
        #         "userPhoneNumber":"+6583234885"
        #     }
        # ]}
        
        # Send to the other exchange
        logger.info(f"Sending to queue: {processed_data}")
        helper_functions.sendToQueue(processed_data)
        logger.info("Message sent to second exchange")
        
        # Acknowledge message only after processing is complete
        logger.info(f"Acknowledging message with delivery tag: {method.delivery_tag}")
        channel.basic_ack(delivery_tag=method.delivery_tag)
        logger.info("Message acknowledged")
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        logger.error(f"Raw message: {body}")
        # Reject message if it's not valid JSON (don't requeue)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        logger.info("Invalid message rejected (not requeued)")
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # For other errors, you might want to requeue the message
        # Set requeue=True if you want to try processing it again
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        logger.info("Error occurred, message rejected (not requeued)")




if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        # Connect to scenario2NotifyExchange
        helper_functions.connectAMQP()

        # Subscribe to scenario12Exchange
        connection, channel = amqp_lib.connect(
            hostname=RABBIT_HOST,
            port=RABBIT_PORT,
            exchange_name=RABBIT_SUBSCRIBER_EXCHANGE,
            exchange_type=RABBIT_SUBSCRIBER_EXCHANGE_TYPE,
        )
        
        # Set to limit 1 message at a time
        channel.basic_qos(prefetch_count=1)
        
        # Start consuming data from scenario12Exchange with manual acknowledgment
        amqp_lib.start_consuming(
            RABBIT_HOST, RABBIT_PORT, RABBIT_SUBSCRIBER_EXCHANGE, 
            RABBIT_SUBSCRIBER_EXCHANGE_TYPE, RABBIT_SUBSCRIBER_QUEUE, 
            callback, auto_ack_status=False
        )
    
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n{exception}\n")