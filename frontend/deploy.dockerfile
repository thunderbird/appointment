FROM nginx:stable

# Copy over files
COPY . /build/frontend

# Copy over the staging config
RUN mv /build/frontend/.env.staging.example /build/frontend/.env.staging

# Add Node 18 support
RUN apt-get install -y ca-certificates curl gnupg1 gnupg2
RUN mkdir -p /etc/apt/keyrings
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
RUN apt-get update
RUN apt-get install -y nodejs

RUN npm install --global yarn

# Build site
RUN cd /build/frontend && yarn install
RUN cd /build/frontend && yarn build -- --mode stage

# Use our custom nginx config
RUN rm /etc/nginx/conf.d/default.conf
COPY docker/etc/nginx/conf.d/appointments.conf /etc/nginx/conf.d/default.conf

RUN cp -r /build/frontend/dist/. /usr/share/nginx/html

EXPOSE 80
