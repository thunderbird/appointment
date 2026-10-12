# Build stage: Node 24 (matches the CI Node; pnpm 11 and vite 8 both require
# Node >=22.13). Only the built dist/ leaves this stage.
FROM node:24-bookworm-slim AS build

WORKDIR /build/frontend

# .dockerignore keeps node_modules, dist, .git and real .env files out of this copy.
COPY . .

# Build site (env-agnostic; runtime config supplies environment values). pnpm
# install --frozen-lockfile for a reproducible, lockfile-pinned install across
# both arch builds.
RUN corepack enable \
    && pnpm install --frozen-lockfile \
    && pnpm run build

# Runtime stage: nginx as an unprivileged user (uid 101) listening on 8080.
FROM nginxinc/nginx-unprivileged:stable

# NOTE: no per-env .env is baked. The SPA is configured at RUNTIME via /config.js
# (see public/config.js + docker-entrypoint.d/40-appointment-config.sh), so one
# built bundle runs unchanged in every environment.

# jq is used by the runtime-config entrypoint to emit JSON-safe config.js.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends jq \
    && rm -rf /var/lib/apt/lists/*

# Use our custom nginx config. Group-writable by nginx so the entrypoint can
# rewrite the API upstream at startup.
COPY --chown=101:0 --chmod=0664 docker/etc/nginx/conf.d/appointments.conf /etc/nginx/conf.d/default.conf

# Runtime config generator: the nginx image runs /docker-entrypoint.d/*.sh at startup,
# writing an env-specific /usr/share/nginx/html/config.js from APP_* env vars.
COPY --chmod=0755 docker/docker-entrypoint.d/40-appointment-config.sh /docker-entrypoint.d/40-appointment-config.sh

# The site is read-only to nginx except for config.js, which the entrypoint
# regenerates at startup.
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /build/frontend/dist/ /usr/share/nginx/html/
RUN chown 101:0 /usr/share/nginx/html/config.js

USER 101

EXPOSE 8080
