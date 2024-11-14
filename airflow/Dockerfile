FROM apache/airflow:2.10.1

#WORKDIR /app

#ENV AIRFLOW_HOME=/app/airflow

# Switch to root user to change permissions
USER root

# Install only the essential dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    chromium \
    chromium-driver \
    xvfb \
    libnss3 \
    libxss1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Copy entrypoint script
# COPY ./entrypoint.sh .

# Make the script executable
# RUN chmod +x ./entrypoint.sh

# Switch to airflow
USER airflow

COPY ./requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# Set the entrypoint
# ENTRYPOINT ["./entrypoint.sh"]