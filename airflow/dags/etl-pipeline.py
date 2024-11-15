from datetime import datetime, timedelta

from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.models.variable import Variable
from airflow.models.dag import DAG
from airflow.models import DagModel
from airflow.providers.postgres.hooks.postgres import PostgresHook
from utilities.ETLScraper import extract
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
    'etl_pipeline',
    default_args=default_args,
    description='ETL pipeline using Selenium and Airflow with CeleryExecutor',
    schedule_interval='*/2 * * * *',  # every 2 minutes
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
) as etl_dag:

    @task.branch(task_id='etl_branch')
    def etl_branch_func():
        pg_hook = PostgresHook(postgres_conn_id='dag_connection')
        connection = pg_hook.get_conn()
        cursor = connection.cursor()

        get_query = """
                    SELECT COUNT(*) from etl_backlog
                    """
        cursor.execute(get_query)
        count = cursor.fetchone()[0]

        if count == 0:
            return "pause_etl_execution"
        else:
            return "extract_data"

    def pause_execution():
        dag: DagModel = DagModel.get_dagmodel('etl_pipeline')
        dag.set_is_paused(True)

        # Save time at which we have finished processing the Backlog
        current_time = datetime.now()
        datetime_string = current_time.strftime("%Y-%m-%d %H:%M:%S")
        Variable.set("time_etl_completion", datetime_string)

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract,
    )

    pause_task = PythonOperator(
        task_id='pause_etl_execution',
        python_callable=pause_execution,
    )

    branch_op = etl_branch_func()

    branch_op >> [pause_task, extract_task]
