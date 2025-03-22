FROM python:3.11-slim

WORKDIR /app

COPY . . 
# copies everything in the hub directory

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "hub.py"]
