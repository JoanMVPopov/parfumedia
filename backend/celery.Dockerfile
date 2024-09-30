# Use Python 3.12.2 image based on Debian Bullseye in its slim variant as the base image
FROM python:3.11.8-slim-bullseye

# Set an environment variable to unbuffer Python output, aiding in logging and debugging
ENV PYTHONBUFFERED=1

## Set the working directory to /app
WORKDIR /app

# install dependencies
RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt


## USE FOR PRODUCTION WHEN READY, OTHERWISE VOLUMES ARE UTILIZED
### Copy the entire backend directory into /app/backend
#COPY . ./backend

ENV PYTHONPATH "${PYTHONPATH}:/app/backend"

CMD celery -A backend.settings.celery worker --loglevel=info