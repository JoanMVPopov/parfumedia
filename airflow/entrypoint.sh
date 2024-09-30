#!/bin/bash

# Initialize the Airflow database
airflow db init

# Create Airflow admin user if it doesn't exist
airflow users create \
  --username "$AIRFLOW_ADMIN_USER" \
  --firstname "$AIRFLOW_ADMIN_FIRSTNAME" \
  --lastname "$AIRFLOW_ADMIN_LASTNAME" \
  --role Admin \
  --email "$AIRFLOW_ADMIN_EMAIL" \
  --password "$AIRFLOW_ADMIN_PASSWORD" \
  || echo "Admin user already exists."

# Start the scheduler in the background
airflow scheduler &

# Start the webserver
exec airflow webserver