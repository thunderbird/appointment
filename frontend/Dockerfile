FROM node:lts-alpine

WORKDIR /app

ENV PATH /app/node_modules/.bin:$PATH

# Get git
RUN apk add --no-cache git

COPY . .
RUN yarn install

CMD vue-cli-service serve