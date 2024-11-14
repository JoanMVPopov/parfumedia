from airflow.decorators import task
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
from tasks.links import link_scrape
from airflow.utils.dates import days_ago
from airflow.models.variable import Variable

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
    schedule_interval='*/10 * * * *',  # every 2 minutes
    catchup=False,
    max_active_runs=1,
) as links_dag:

    @task.branch(task_id="branch")
    def branch_func():
        times_ran = int(Variable.get("get_col_links", default_var=0))

        #print("\n\nTIMES RAN in links-dag: ", times_ran)

        if times_ran < 5:
            return 'link_scraping'
        else:
            return 'empty'

    link_scraping_op = PythonOperator(
        task_id="link_scraping",
        python_callable=link_scrape
    )

    empty_op = EmptyOperator(task_id="empty")

    branch_op = branch_func()

    branch_op >> [link_scraping_op, empty_op]
