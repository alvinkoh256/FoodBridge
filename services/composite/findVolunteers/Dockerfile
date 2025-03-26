FROM python:3.12.9-slim 

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . ./

EXPOSE 5001

ENTRYPOINT [ "python" ]
CMD ["find_volunteers.py"]

# docker run -p 5001:5001 --env-file D:\SMU\Y2S2\ESD\Project\FoodBridge\.env  wongyh01/find_volunteers:1.0
