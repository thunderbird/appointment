FROM nginx:stable

# Copy over files
COPY . /build/frontend

# NOTE: no per-env .env is baked. The SPA is configured at RUNTIME via /config.js
# (see public/config.js + docker-entrypoint.d/40-appointment-config.sh), so one
# built bundle runs unchanged in every environment.

# Add Node 24 (matches the CI Node; pnpm 11 and vite 8 both require Node >=22.13)
# and jq (used by the runtime-config entrypoint to emit JSON-safe config.js).
RUN apt-get update
RUN apt-get install -y ca-certificates curl gnupg jq
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_24.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update
RUN apt-get install -y nodejs

# Build site (env-agnostic; runtime config supplies environment values). pnpm
# install --frozen-lockfile for a reproducible, lockfile-pinned install across
# both arch builds.
RUN corepack enable
RUN cd /build/frontend && pnpm install --frozen-lockfile
RUN cd /build/frontend && pnpm run build

# Use our custom nginx config
RUN rm /etc/nginx/conf.d/default.conf
COPY docker/etc/nginx/conf.d/appointments.conf /etc/nginx/conf.d/default.conf

# Runtime config generator: nginx:stable runs /docker-entrypoint.d/*.sh at startup,
# writing an env-specific /usr/share/nginx/html/config.js from APP_* env vars.
COPY docker/docker-entrypoint.d/40-appointment-config.sh /docker-entrypoint.d/40-appointment-config.sh
RUN chmod +x /docker-entrypoint.d/40-appointment-config.sh

RUN cp -r /build/frontend/dist/. /usr/share/nginx/html

EXPOSE 80
