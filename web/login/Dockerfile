FROM node:23

WORKDIR /app

COPY src/ .
COPY flag.txt /
RUN npm i

CMD ["node", "app.js"]