from airflow.models import Variable, DagModel
from airflow.providers.postgres.hooks.postgres import PostgresHook
from bs4 import BeautifulSoup
import logging
from Driver import ScrapeDriver
from links import links
import pandas as pd


class LinkScraper:
    def __init__(self, driver):
        self.logger = logging.getLogger(__name__)
        self.driver = driver.get_driver()
        self.display = driver.get_display()

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

            times_ran = int(Variable.get("list_links_iterations", default_var=0))
            Variable.set("list_links_iterations", times_ran+1)

            dag: DagModel = DagModel.get_dagmodel('etl_pipeline')
            if dag.is_paused:
                dag.set_is_paused(False)

        except Exception as e:
            connection.rollback()
            print(f"Error inserting records into Backlog: {e}")
        finally:
            cursor.close()
            connection.close()


def link_scrape():
    driver = ScrapeDriver()
    link_scraper = LinkScraper(driver)
    return link_scraper.scrape_links()
