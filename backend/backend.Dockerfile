# Use Python 3.12.2 image based on Debian Bullseye in its slim variant as the base image
FROM python:3.11.8-slim-bullseye

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define an environment variable for the web service's port, commonly used in cloud services
ENV PORT 8000

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

# Print the Python system paths being searched for modules
#RUN python -c "import sys; print('\n'.join(sys.path))" && echo "\n"

# Inform Docker that the container listens on the specified network port at runtime
EXPOSE ${PORT}

CMD python backend/manage.py migrate && gunicorn backend.wsgi:application --bind 0.0.0.0:"${PORT}"

