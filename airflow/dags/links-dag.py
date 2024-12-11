import os

from airflow.decorators import task
from airflow.models import DagModel
from airflow.operators.empty import EmptyOperator
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from airflow import DAG
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging
from pyvirtualdisplay import Display
from utilities.ListLinkScraper import link_scrape
from airflow.utils.dates import days_ago
from airflow.models.variable import Variable
from sshtunnel import SSHTunnelForwarder
import psycopg2

default_args = {
    'start_date': days_ago(0),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id="links",
    default_args=default_args,
    description='DAG to scrape 400 links (4*100) up to 5 times',
    # schedule_interval='0 */12 * * *',  # every 12 hours
    schedule_interval='*/10 * * * *',  # every 10 minutes
    catchup=False,
    max_active_runs=1,
) as links_dag:

    @task.branch(task_id="branch")
    def branch_func():
        times_ran = int(Variable.get("list_links_iterations", default_var=0))

        dag: DagModel = DagModel.get_dagmodel('etl_pipeline')
        if not dag.is_paused:
            return 'list_empty'

        # if times_ran < 5:
        if times_ran < 3:
            return 'link_scraping'
        else:
            return 'handle_rescheduling'

    def handle_rescheduling():
        # TODO: Need to figure out a default return value
        time_etl_completion = datetime.strptime(Variable.get("time_etl_completion"), "%Y-%m-%d %H:%M:%S")
        # delta = timedelta(days=5) or (days=7)
        delta = timedelta(minutes=5)

        # TODO: What happens if you reschedule scraping while etl-pipeline is running?
        # This behaviour should be avoided, good weather does not allow it, but further testing needed
        # Possibly include dag.is_paused check in here
        if abs(time_etl_completion - datetime.now()) >= delta:
            print(f"Elapsed time between last total scrape job and now exceeds ${delta}. Scraping will resume soon...")
            Variable.set("list_links_iterations", 0)

            try:
                # SSH Tunnel Configuration
                bastion_host = os.getenv('BASTION_PUBLIC_IP')  # Replace with your bastion host public IP
                bastion_username = 'ec2-user'
                ssh_pkey = os.getenv('SSH_PKEY', '/root/.ssh/coolify_bastion_key')  # Path to your private key
                remote_bind_host = os.getenv('RDS_HOST')
                remote_bind_port = 5432
                local_bind_port = 6000  # Local port for the SSH tunnel

                # RDS Database Credentials
                remote_db_name = 'postgres'
                remote_db_user = 'postgres'
                remote_db_password = os.getenv('RDS_PASSWORD')  # Replace with the actual password

                # Establish SSH Tunnel
                with SSHTunnelForwarder(
                        (bastion_host, 22),
                        ssh_username=bastion_username,
                        ssh_pkey=ssh_pkey,
                        remote_bind_address=(remote_bind_host, remote_bind_port),
                        local_bind_address=('localhost', local_bind_port)
                ) as tunnel:
                    pg_hook = PostgresHook(postgres_conn_id='dag_connection')
                    connection = pg_hook.get_conn()
                    cursor = connection.cursor()

                    # Fetch Rows from Local Table
                    cursor.execute("SELECT * FROM etl_perfume;")
                    rows = cursor.fetchall()

                    print("Number of rows: " + str(len(rows)))
                    print(rows)

                    # Connect to Remote RDS via Tunnel
                    remote_conn = psycopg2.connect(
                        host='localhost',  # Local end of the SSH tunnel
                        port=local_bind_port,
                        dbname=remote_db_name,
                        user=remote_db_user,
                        password=remote_db_password
                    )
                    remote_cur = remote_conn.cursor()

                    print("AFTER REMOTE CONN")

                    # TODO: Determine ON CONFLICT behaviour

                    # Insert Data into Remote Table
                    insert_query = """
                    INSERT INTO etl_perfume (id, link, name, brand, rel_year, rel_decade, notes, chart_categories, 
                            chart_numbers, scent, longevity, sillage, bottle, value_for_money)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """
                    remote_cur.executemany(insert_query, rows)
                    remote_conn.commit()

                    print("Successfully transferred data to Amazon RDS instance")

            except Exception as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                connection.close()
                remote_cur.close()
                remote_conn.close()

            return
        else:
            print(f"Waiting time of ${delta} not reached. No actions will be taken until then...")
            return


    link_scraping_op = PythonOperator(
        task_id="link_scraping",
        python_callable=link_scrape
    )


    handle_rescheduling_op = PythonOperator(
        task_id="handle_rescheduling",
        python_callable=handle_rescheduling
    )

    empty_op = EmptyOperator(task_id="list_empty")

    branch_op = branch_func()

    branch_op >> [empty_op, link_scraping_op, handle_rescheduling_op]
