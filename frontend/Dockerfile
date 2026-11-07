FROM node:24-alpine

# Get git
RUN apk add --no-cache git

# corepack writes shims into /usr/local/bin, so enable it before dropping root.
RUN corepack enable

WORKDIR /app
RUN chown node:node /app

ENV PATH="/app/node_modules/.bin:${PATH}"

# Run as the image's unprivileged `node` user (uid 1000).
USER node

# Only the install manifests: docker-compose bind-mounts the source over /app.
COPY --chown=node:node package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

CMD ["vite", "dev", "--port", "8080"]
