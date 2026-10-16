# stage 1: build the react app with node
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# stage 2: serve the built files with nginx
# nginx-unprivileged runs as user 101 (not root) and listens on 8080
FROM nginxinc/nginx-unprivileged:1.30.5-alpine

# backend address, docker compose uses this default, helm overrides it
ENV BACKEND_URL=http://backend:8000
# lets the nginx template use the dns server from /etc/resolv.conf
ENV NGINX_ENTRYPOINT_LOCAL_RESOLVERS=1

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

USER 101
EXPOSE 8080
