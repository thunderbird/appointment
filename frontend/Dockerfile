FROM node:lts-alpine

# Get git
RUN apk add --no-cache git

# corepack writes shims into /usr/local/bin, so enable it before dropping root.
RUN corepack enable

WORKDIR /app
RUN chown node:node /app

ENV PATH="/app/node_modules/.bin:${PATH}"

# Run as the image's unprivileged `node` user (uid 1000).
USER node

COPY --chown=node:node . .
RUN pnpm install --frozen-lockfile

CMD ["vite", "dev", "--port", "8080"]
