from airflow.models import Variable, DagModel
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
import pandas as pd

links = ["https://www.parfumo.com/s_perfumes_x.php?current_page=1&v=list&o=nr_desc&g_f=1&g_m=1&g_u=1&y_t=2&y_3=2020&n_t=1",
         "https://www.parfumo.com/s_perfumes_x.php?current_page=1&v=list&o=nr_desc&g_f=1&g_m=1&g_u=1&y_t=2&y_3=2010&n_t=1",
         "https://www.parfumo.com/s_perfumes_x.php?current_page=1&v=list&o=nr_desc&g_f=1&g_m=1&g_u=1&y_t=2&y_3=2000&n_t=1",
         "https://www.parfumo.com/s_perfumes_x.php?current_page=1&v=list&o=nr_desc&g_f=1&g_m=1&g_u=1&y_t=2&y_3=1990&n_t=1"]

class LinkScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver, self.display = self.setup_driver()

    def setup_driver(self):
        display = Display(visible=False, size=(1920, 1080))
        display.start()

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        return driver, display

    def scrape_links(self):
        target_links = []

        for link in links:
            self.driver.get(link)

            html = self.driver.page_source

            soup = BeautifulSoup(html, 'html.parser')

            items = soup.find_all('div', class_="col-list")

            for item in items:
                div_name_tag = item.find("div", class_="name")
                a_tag = div_name_tag.find("a")
                target_link = a_tag['href']
                target_links.append((target_link, 0))

        self.driver.quit()
        self.display.stop()

        # df = pd.DataFrame(columns=["Link"], data=target_links)

        # Use the created connection ID
        pg_hook = PostgresHook(postgres_conn_id='dag_connection')
        connection = pg_hook.get_conn()
        cursor = connection.cursor()

        try:
            # Insert scraped URLs into Backlog
            insert_query = """
                INSERT INTO etl_backlog (link, attempts)
                VALUES (%s, %s);
                """

            cursor.executemany(insert_query, target_links)
            connection.commit()

            times_ran = int(Variable.get("get_col_links", default_var=0))
            #print("\n\nTIMES RAN in links: ", times_ran)
            Variable.set("get_col_links", times_ran+1)
            #print("SET TO", times_ran + 1)

            dag2: DagModel = DagModel.get_dagmodel('etl-pipeline')
            if dag2.is_paused:
                dag2.set_is_paused(False)

        except Exception as e:
            connection.rollback()
            print(f"Error inserting records into Backlog: {e}")
        finally:
            cursor.close()
            connection.close()


def link_scrape():
    link_scraper = LinkScraper()
    return link_scraper.scrape_links()