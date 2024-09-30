# Exit immediately if a command exits with a non-zero status
set -e

# Change to the directory where the script is located (project root)
cd "$(dirname "$0")"

# Activate Python virtual environment
source .venv/Scripts/activate

# Confirm activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "Virtual environment not activated.\n"
    exit 1
else
    echo -e "Virtual environment activated at: $VIRTUAL_ENV\n"
fi

# Set AIRFLOW_HOME to a directory within your project
AIRFLOW_HOME=$(pwd)/airflow
export AIRFLOW_HOME

# Function to kill all child processes upon exit
cleanup() {
    echo "Stopping servers..."
    kill 0
    exit
}

# Trap SIGINT (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# Initialize Airflow if not already initialized
if [ ! -d "$AIRFLOW_HOME" ]; then
    echo -e "Initializing Airflow...\n"
    airflow db init

    # Create necessary Airflow directories
    mkdir -p "$AIRFLOW_HOME/dags"
    mkdir -p "$AIRFLOW_HOME/logs"
    mkdir -p "$AIRFLOW_HOME/plugins"

    echo -e "Airflow initialization complete.\n"
fi

# Start Django server in the background
echo -e "Starting Django server...\n"
python manage.py runserver &

# Start Airflow scheduler in the background
echo -e "Starting Airflow scheduler...\n"
airflow scheduler &

# Wait for all background processes to finish
wait