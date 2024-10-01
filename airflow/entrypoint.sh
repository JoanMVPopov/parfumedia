#!/bin/bash

printenv

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

# Wait until the DAG is registered
echo "Waiting for DAG 'etl-pipeline' to be registered..."
while ! airflow dags list | grep -w 'etl-pipeline'; do
  sleep 5
done
echo "DAG 'etl-pipeline' is now registered."

# Trigger the DAG programmatically using the Airflow CLI
airflow dags trigger etl-pipeline

# Start the webserver in the foreground (this keeps the container alive)
exec airflow webserver