from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email': ['mamaegalabar4@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl-pipeline',
    default_args=default_args,
    description='ETL pipeline using Selenium and Airflow with CeleryExecutor',
    schedule_interval=timedelta(seconds=10),
    start_date=datetime(2024, 10, 1),
    # Determines whether Airflow should backfill
    # missed DAG runs between the start_date and the current date.
    catchup=False,
)

def extract_data(**context):
    print("Extracting")
    pass

def transform_data(**context):
    print("Transforming")
    pass

def load_data(**context):
    print("Loading data")
    pass

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_task',
    python_callable=load_data,
    dag=dag
)

extract_task >> transform_task >> load_task
