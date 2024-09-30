FROM apache/airflow:2.10.1

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Switch to root user to change permissions
USER root

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh

# Make the script executable
RUN chmod +x /entrypoint.sh

# Switch to airflow
USER airflow

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]