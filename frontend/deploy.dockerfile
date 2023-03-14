FROM nginx:stable

# Copy over files
COPY . /build/frontend

# Add Node 16 support
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash - &&\
apt-get install -y nodejs

# Build site
RUN cd /build/frontend && npm install
RUN cd /build/frontend && npm run build

# Use our custom nginx config
RUN rm /etc/nginx/conf.d/default.conf
COPY docker/etc/nginx/conf.d/appointments.conf /etc/nginx/conf.d/default.conf

COPY docker/etc/nginx/.htpasswd /etc/nginx/.htpasswd

RUN cp -r /build/frontend/dist/. /usr/share/nginx/html

EXPOSE 80