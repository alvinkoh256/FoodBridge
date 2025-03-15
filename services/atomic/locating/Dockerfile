FROM python:3.12.9-slim 

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY *py ./

EXPOSE 5003
CMD ["uvicorn", "locating:app", "--host", "0.0.0.0", "--port", "5003"]

# docker run -p 5003:5003 --env-file D:\SMU\GitRepos\FoodBridge\.env  wongyh01/locating:1.0
