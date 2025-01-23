FROM node:lts-alpine

WORKDIR /app

ENV PATH="/app/node_modules/.bin:${PATH}"

# Get git
RUN apk add --no-cache git

COPY . .
RUN npm install

CMD ["vite", "dev", "--port", "8080"]
