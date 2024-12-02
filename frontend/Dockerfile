# frontend/Dockerfile

# Stage 1: Build
FROM node:16 AS build

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install

COPY . .

RUN yarn build

# Stage 2: Serve
FROM nginx:stable-alpine

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Copy the custom Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d

# Copy the build output to Nginx html directory
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
