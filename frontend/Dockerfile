#FROM node:lts-alpine

FROM node:14-alpine

RUN npm cache clean --force

# install simple http server for serving static content
RUN npm install -g http-server --verbose

# make the 'app' folder the current working directory
WORKDIR /app

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# install project dependencies
RUN npm install

#----------

## USING VOLUMES RIGHT NOW, CHANGE TO THIS LATER FOR PRODUCTION
## copy project files and folders to the current working directory (i.e. 'app' folder)
#COPY . ./frontend

## build app for production with minification
#RUN npm run build
#
#EXPOSE 8080
#CMD [ "http-server", "dist" ]

#-----------

# build app for production with minification

## THIS WORKS, USING PRODUCTION APPROACH WHILE UTILIZING VOLUMES
## BUT BUILDING WHILE RUNNING A CONTAINER IS NOT A GOOD IDEA, SLOW
## BETTER TO DO IT WHEN BUILDING IMAGE (with RUN npm run build above)

#EXPOSE 8080
#CMD cd ./frontend && npm run build && http-server dist

EXPOSE 8080
CMD cd ./frontend && npm run serve