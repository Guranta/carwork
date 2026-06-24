FROM node:20-alpine AS build

WORKDIR /app
COPY h5/package*.json ./
RUN npm ci

COPY h5/ ./
RUN npm run build

FROM nginx:alpine

COPY deploy/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
