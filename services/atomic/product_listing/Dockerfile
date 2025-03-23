FROM node:20-slim

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY *.js ./

EXPOSE 5005

CMD ["node", "app.js"]

# docker run -p 5005:5005 --env-file .env  wongyh01/product_listing:1.0