# AMQP Setup for RabbitMQ

This directory contains the configuration and setup for **RabbitMQ**, including exchanges, queues, and bindings used by the application. The setup is automated using the **`amqp-setup`** service in **Docker Compose**.

### How RabbitMQ is Used in Our Project

RabbitMQ acts as the messaging broker for asynchronous communication between microservices. It allows services to publish messages to exchanges and consume messages from queues.

### How the AMQP Setup Works

- The **`amqp-setup`** service is part of our Docker Compose setup. When you run `docker-compose up`, this service will automatically:
  1. **Create the required exchanges** in RabbitMQ.
  2. **Create the required queues** in RabbitMQ.
  3. **Bind the queues to the exchanges** with routing keys.

---

### Adding a New Queue

If you need to add a new queue to RabbitMQ, follow these steps:

#### Step 1: Define the Queue Name

Decide on the name for the new queue. For example, if you want to create a queue for **user registrations**, you might name it `user_registration_queue`.

#### Step 2: Modify the `amqp_setup.py` Script

1. **Declare the Exchange**: First, ensure that the **exchange** to which the queue will bind is declared. If you're using an existing exchange (e.g., `order_topic`), you can skip this. If it's a new exchange, declare it by adding the following to `amqp_setup.py`:

    ```python
    # Declare the exchange (if it's a new one)
    channel.exchange_declare(exchange='your_exchange_name', exchange_type='topic')
    ```

2. **Declare the Queue**: Add the following code to declare the new queue and bind it to the exchange:

    ```python
    # Declare the new queue
    channel.queue_declare(queue='user_registration_queue', durable=True)
    
    # Bind the queue to the exchange with a routing key
    channel.queue_bind(exchange='your_exchange_name', queue='user_registration_queue', routing_key='user.registration.*')
    ```

    - Replace `'user_registration_queue'` with your queue name.
    - Adjust the `routing_key` as needed based on which messages this queue should receive.

#### Step 3: Run the AMQP Setup

Once the queue has been added to `amqp_setup.py`, run the **AMQP setup** script by bringing up the services with Docker Compose:

```bash
docker-compose up --build
```

- The `amqp-setup` service will automatically run the **`amqp_setup.py`** script to configure RabbitMQ.
- The queue and exchange will be created, and the queue will be bound to the exchange with the routing key.

#### Step 4: Verify in RabbitMQ Management UI

Once the setup script runs, you can verify the new queue and exchange in the **RabbitMQ Management UI**:

- **UI URL**: `http://localhost:15672`
- **Login**: Use the default credentials (`guest` / `guest`).

Here you can monitor the queues, exchanges, and bindings to ensure the new configuration is correct.

---

### Example of `amqp_setup.py` Script

Here is the complete script that handles declaring exchanges, queues, and binding them:

```python
import pika

def setup_amqp():
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    # Declare the exchange
    channel.exchange_declare(exchange='order_topic', exchange_type='topic')

    # Declare and bind a queue
    channel.queue_declare(queue='order_queue', durable=True)
    channel.queue_bind(exchange='order_topic', queue='order_queue', routing_key='order.*')

    print("AMQP setup completed!")
    connection.close()

if __name__ == '__main__':
    setup_amqp()
```

This script:
- Declares an exchange (`order_topic`).
- Declares a queue (`order_queue`).
- Binds the queue to the exchange with a routing key (`order.*`).

---

### Additional Notes

- **Durable Queues**: Make sure to set `durable=True` when declaring queues and exchanges if you want them to survive RabbitMQ restarts.
- **Exchange Types**: RabbitMQ supports different exchange types like `direct`, `topic`, `fanout`, and `headers`. Use the appropriate one depending on your use case.
- **Routing Keys**: The routing key determines which messages the queue will receive. Ensure that it is set correctly based on the message patterns you want to handle.
