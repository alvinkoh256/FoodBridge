FROM python:3.11.9-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY *.py *.txt ./

ENV RABBITMQ_HOST=localhost
ENV RABBITMQ_PORT=5672
ENV RABBITMQ_USER=guest
ENV RABBITMQ_PASS=guest

ENTRYPOINT ["python"]
CMD ["callback.py"]

