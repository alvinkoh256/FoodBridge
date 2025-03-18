# RabbitMQ Setup & Usage Guide

This guide will walk you through the steps to **create new exchanges**, **create new queues**, and **publish and consume messages** from RabbitMQ using the shared `amqp_lib.py` utility library.

---

## **Steps to Set Up a New Exchange and Queue**

### **Step 1: Create a New Exchange**
1. Open **`amqp_setup.py`** in your service directory.
2. To **declare a new exchange**, uncomment and customize the line for `create_exchange` based on the **exchange type** you want:

   - **Topic Exchange**: For routing based on patterns (e.g., `"order.*"`).
   - **Direct Exchange**: For routing based on an exact match (e.g., `"order.created"`).
   - **Fanout Exchange**: For broadcasting to all queues bound to the exchange (no routing key needed).

   **Example for Topic Exchange**:
   ```python
   create_exchange(channel, "topic_exchange", "topic")  # Topic exchange for routing
   ```

   **Example for Direct Exchange**:
   ```python
   create_exchange(channel, "direct_exchange", "direct")  # Direct exchange for exact routing
   ```

   **Example for Fanout Exchange**:
   ```python
   create_exchange(channel, "fanout_exchange", "fanout")  # Fanout exchange for broadcasting
   ```

### **Step 2: Create a New Queue**
1. Next, you need to **create a new queue** and bind it to the exchange you just declared.

   - Choose the **queue name** and **routing key** (if needed).
   - Use the **exchange type** you created in **Step 1** to bind the queue to the exchange.

   **Example for Topic Exchange** (with a routing key):
   ```python
   create_queue(channel, "topic_exchange", "order_queue", "order.*")
   ```

   **Example for Fanout Exchange** (no routing key):
   ```python
   create_queue(channel, "fanout_exchange", "broadcast_queue", "")
   ```

   **Example for Direct Exchange** (with an exact routing key):
   ```python
   create_queue(channel, "direct_exchange", "specific_order_queue", "order.created")
   ```

---

## **Steps to Publish and Consume Messages**

### **Step 3: Import `amqp_lib` in Your Service**
1. Import the **`amqp_lib.py`** in your service's Python file:

   ```python
   from services.amqp_lib.amqp_lib import publish_message, consume_message
   ```

### **Step 4: Publishing a Message**

To **publish a message** to an exchange, use the `publish_message` function from `amqp_lib.py`.

1. **Add the following code to your service** to publish a message:

   ```python
   # Example of publishing a message to RabbitMQ
   publish_message('topic_exchange', 'order.created', 'This is a new order.')
   ```

   - **`'topic_exchange'`**: The name of the exchange.
   - **`'order.created'`**: The routing key (you can use any key that matches the exchange's routing rules).
   - **`'This is a new order.'`**: The actual message content.

   This will send the message to the **`topic_exchange`** with the routing key **`order.created`**.

### **Step 5: Consuming a Message**

To **consume messages** from a queue, use the `consume_message` function from `amqp_lib.py`.

1. **Add the following code** in your service to consume messages from a queue:

   ```python
   # Example callback function to process messages
   def callback(ch, method, properties, body):
       print(f"Received message: {body.decode()}")
       # Add your logic here to process the message, like saving to a database
       # For example:
       # process_order_data(body.decode())

   # Start consuming from the 'order_queue' queue
   consume_message('order_queue', callback)
   ```

   - **`callback(ch, method, properties, body)`**: This function is triggered every time a message is received. The `body` contains the message, and you can add your own processing logic inside the callback.
   - **`'order_queue'`**: The name of the queue to consume from.

---

## **Important Notes:**

- **Durability**: Ensure that both the **exchange** and **queue** are declared with `durable=True` if you want them to survive RabbitMQ restarts.
- **Routing Key**: Only **topic** and **direct** exchanges use a **routing key**. Fanout exchanges send the message to all bound queues without considering a routing key.
- **Error Handling**: Make sure to handle errors gracefully, such as when the connection to RabbitMQ fails or the queue does not exist.
  
---

## **Example Workflow:**

Let's say you need to create a **new queue for order updates** that binds to a **topic exchange**.

1. In **`amqp_setup.py`**, add the following:
   ```python
   # Declare a topic exchange
   create_exchange(channel, "topic_exchange", "topic")  # Topic exchange for routing

   # Declare a queue for orders with routing key "order.*"
   create_queue(channel, "topic_exchange", "order_updates_queue", "order.*")
   ```

2. In your **service file**, import `amqp_lib.py` and add the logic to **consume messages**:

   ```python
   from services.amqp_lib.amqp_lib import consume_message

   # Define the callback to process the message
   def callback(ch, method, properties, body):
       print(f"Received order update: {body.decode()}")
       # Process the order update here...

   # Start consuming from the "order_updates_queue"
   consume_message('order_updates_queue', callback)
   ```

---

### **Summary**:

- **Step 1**: Declare the **exchange** in `amqp_setup.py`.
- **Step 2**: Declare the **queue** and bind it to the exchange.
- **Step 3**: In your service, **import `amqp_lib.py`** to reuse connection and message handling functions.
- **Step 4**: **Publish messages** to RabbitMQ using `publish_message()` from `amqp_lib.py`.
- **Step 5**: **Consume messages** from RabbitMQ by defining a **callback** function and using `consume_message()` from `amqp_lib.py`.