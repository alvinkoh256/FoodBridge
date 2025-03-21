## How to Add a New Messaging Event (RabbitMQ)

Follow these steps when you want your service to **publish or subscribe** to a new RabbitMQ event.

Refer to testPublisher and testSubscriber under atomic/services if you need reference. If you still need help with integrating this into your service, please reach out to me! - Alvin

---

### 1. Update `amqp_setup.py`

This sets up the required **exchange**, **queue**, and **binding**.

#### Add the following block:
```python
<new_channel_name> = create_exchange(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name="<new_exchange_name>",
    exchange_type="<exchange_type>",  # e.g. 'topic', 'direct', 'fanout'
)

create_queue(
    channel=<new_channel_name>,
    exchange_name="<new_exchange_name>",
    queue_name="<queue_name>",
    routing_key="<routing_key>"
)
```

**Replace:**
- `<new_channel_name>` – any variable name (e.g. `channelOrders`)
- `<new_exchange_name>` – name of your exchange (e.g. `orderExchange`)
- `<exchange_type>` – typically `topic`, `direct`, or `fanout`
- `<queue_name>` – name of your queue (e.g. `OrderCreatedQueue`)
- `<routing_key>` – message routing key (e.g. `order.created`)

---
### 2. Copy paste amqp_lib.py from root into your service folder

---

### 3. Update Dockerfile in your service folder OR add pika to requirements

This ensures your service has `pika` and `amqp_lib.py`.

#### Example:
```dockerfile
FROM python:3.9
WORKDIR /app

COPY . /app/
RUN pip install pika (or just add pika to your requirements.txt)

CMD ["python3", "<your_service_script>.py"]
```

Replace `<your_service_script>.py` with your actual Python filename.

---

### 4. Update Your Python Service Code

#### If You’re a **Publisher**:
```python
import amqp_lib

rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "<new_exchange_name>"
exchange_type = "<exchange_type>"
routing_key = "<routing_key>"

message = {"data": "Your message payload"}

amqp_lib.publish_message(
    hostname=rabbit_host,
    port=rabbit_port,
    exchange_name=exchange_name,
    exchange_type=exchange_type,
    routing_key=routing_key,
    message=message
)
```

#### If You’re a **Subscriber**:
```python
import amqp_lib

rabbit_host = "rabbitmq"
rabbit_port = 5672
exchange_name = "<new_exchange_name>"
exchange_type = "<exchange_type>"
queue_name = "<queue_name>"

def callback(ch, method, properties, body):
    print(f"[x] Received: {body.decode()}")

amqp_lib.start_consuming(
    rabbit_host,
    rabbit_port,
    exchange_name,
    exchange_type,
    queue_name,
    callback
)
```

---

### 5. Add `depends_on` in `docker-compose.yml` (if needed)

This ensures your service starts **after RabbitMQ & AMQP setup**.

```yaml
  <your_service_name>:
    build:
      context: ./services/<path_to_your_service>
      dockerfile: Dockerfile
    depends_on:
      - amqp-setup
    networks:
      - esd-net
```

### 6. Test the messaging functionality

1. docker compose up
2. amqp_setup.py will only run the first time, and the container will stop right after (it works like that so don't be alarmed!).
3. check the container logs for publisher and subscriber service to see if it works.
4. Any issues? Contact me! - Alvin