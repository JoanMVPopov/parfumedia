from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.models.variable import Variable
from airflow.models.dag import DAG
from airflow.models import DagModel
from tasks.load import load
from tasks.extract import extract
from tasks.transform import transform
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'email': ['mamaegalabar4@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'start_date': days_ago(0)
}

with DAG(
    'etl-pipeline',
    default_args=default_args,
    description='ETL pipeline using Selenium and Airflow with CeleryExecutor',
    schedule_interval='*/2 * * * *',  # every 2 minutes
    catchup=False,
    max_active_runs=1,
) as etl_dag:

    # dag.set_is_paused(True)

    # dag2: DagModel = DagModel.get_dagmodel('etl-pipeline')
    # dag2.set_is_paused(True)

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract,
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id='load_task',
        python_callable=load,
    )

    extract_task >> transform_task >> load_task
