# build stage
FROM node:14-alpine AS build-stage

RUN npm cache clean --force

WORKDIR /app

# inject all environment vars we'll need
ARG VUE_APP_API_URL
# expose the variable to the finished cotainer
ENV VUE_APP_API_URL=$VUE_APP_API_URL

COPY package*.json ./
RUN npm install --verbose
COPY . .
RUN npm run build

# production stage
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]