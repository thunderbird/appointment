FROM node:lts-alpine

WORKDIR /app

ENV PATH="/app/node_modules/.bin:${PATH}"

# Get git
RUN apk add --no-cache git

COPY . .
RUN corepack enable && pnpm install --frozen-lockfile

CMD ["vite", "dev", "--port", "8080"]
