FROM python:3.12.9-slim 

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY *py ./

EXPOSE 5006
CMD ["python", "locating.py"]

# docker run -p 5006:5006 --env-file D:\SMU\GitRepos\FoodBridge\.env  wongyh01/locating:1.0
