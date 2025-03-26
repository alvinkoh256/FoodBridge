FROM python:3.11.9-slim 

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY *py *txt ./

EXPOSE 5004

ENTRYPOINT [ "python" ]
CMD ["product_validation.py"]

# docker run -p 5004:5004 --env-file D:\SMU\GitRepos\FoodBridge\.env  wongyh01/product_validation:1.0
