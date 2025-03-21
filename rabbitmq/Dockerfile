# Use official Python image
FROM python:3.9

# Set working directory inside the container
WORKDIR /app

# Copy amqp_setup.py from rabbitmq/ folder in your project
COPY rabbitmq/amqp_setup.py /app/amqp_setup.py

# Install dependencies
RUN pip install pika

# Run the setup script
CMD ["python3", "/app/amqp_setup.py"]
