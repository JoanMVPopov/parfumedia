FROM apache/airflow:2.10.1

#WORKDIR /app

#ENV AIRFLOW_HOME=/app/airflow

RUN env

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Switch to root user to change permissions
USER root

# Copy entrypoint script
COPY ./entrypoint.sh .

# Make the script executable
RUN chmod +x ./entrypoint.sh

# Switch to airflow
USER airflow

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]