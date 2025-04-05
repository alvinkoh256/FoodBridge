FROM python:3.12.9-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY *py . 

EXPOSE 5007
CMD ["uvicorn", "notification_service:app", "--host", "0.0.0.0", "--port", "5007"] 
