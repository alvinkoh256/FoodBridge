FROM node:20-slim

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY *.js ./

EXPOSE 5014

# Command to run the application
CMD ["node", "websocket.js"]


# docker run -p 5014:5014 wongyh01/websocket:1.0
