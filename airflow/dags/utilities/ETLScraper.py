import logging

from airflow.providers.postgres.hooks.postgres import PostgresHook
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from utilities.generic.Driver import ScrapeDriver


class Scraper:
    def __init__(self, driver):
        self.logger = logging.getLogger(__name__)
        self.driver_instance = driver

    def create_soup(self, link, index):
        self.driver_instance.driver.get(link)

        if index == 0:
            try:
                # Handle consent message
                iframe_title = "SP Consent Message"
                iframe_xpath = f"//iframe[@title='{iframe_title}']"

                iframe = (WebDriverWait(self.driver_instance.driver, 5)
                          .until(EC.presence_of_element_located((By.XPATH, iframe_xpath))))

                self.driver_instance.driver.switch_to.frame(iframe)

                button_title = "Accept"
                button_xpath = f"//button[@title='{button_title}']"

                button = (WebDriverWait(self.driver_instance.driver, 5)
                          .until(EC.presence_of_element_located((By.XPATH, button_xpath))))

                button.click()

            except TimeoutException:
                print("No consent message detected. Moving on...")
            except Exception as e:
                print(f"Unexpected error occurred: {e}")
            finally:
                self.driver_instance.driver.switch_to.default_content()

        # Show pie charts and prepare soup
        chart_button_xpath = "/html/body/div[5]/div/div[1]/div[1]/nav/div[6]/span"

        chart_button = (WebDriverWait(self.driver_instance.driver, 10)).until(EC.presence_of_element_located((By.XPATH, chart_button_xpath)))
        chart_button.click()

        # Wait until data shows up
        WebDriverWait(self.driver_instance.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'resize-sensor')))

        html = self.driver_instance.driver.page_source

        return BeautifulSoup(html, "html.parser")

    def extract_notes(self, soup, data_dic):
        notes = soup.find_all('span', class_="nowrap pointer")
        note_list = []

        for item in notes:
            item_text = item.get_text(strip=True)
            note_list.append(item_text)

        data_dic['Notes'] = note_list
        return data_dic

    def extract_chart_items(self, soup, data_dic):
        chart_items = soup.find_all('div', class_="col mb-2")
        chart_categories_only_chart_list = []
        chart_numbers_only_chart_list = []

        for item in chart_items:
            current_chart_items = item.find_all('tspan')

            # For each span in the current item
            for i in current_chart_items:
                item_text = i.get_text(strip=True)
                if item_text == '100%':
                    continue
                split_text = item_text.rsplit(' ', 1)
                chart_categories_only_chart_list.append(split_text[0])
                chart_numbers_only_chart_list.append(int(split_text[1].split("%")[0]))

        data_dic['Chart Categories'] = chart_categories_only_chart_list
        data_dic['Chart Numbers'] = chart_numbers_only_chart_list
        return data_dic

    def is_float(self, s):
        try:
            float(s)
            return True
        except (ValueError, TypeError):
            return False

    def extract_rating_items(self, soup, data_dic):
        rating_items = soup.find_all('div', class_="flex flex-wrap")

        current_rating_item = rating_items[0].get_text(separator=' ')
        current_rating_item = [float(x) for x in current_rating_item.split() if self.is_float(x)]
        current_rating_item = current_rating_item[
                              0:len(current_rating_item):2]  # only select 1-10 ratings, categories known
        data_dic['Scent'] = current_rating_item[0]
        data_dic['Longevity'] = current_rating_item[1]
        data_dic['Sillage'] = current_rating_item[2]
        data_dic['Bottle'] = current_rating_item[3]
        data_dic['Value For Money'] = current_rating_item[4]

        return data_dic

    def extract_general(self, soup, data_dic):
        general_div = soup.find("div", class_="p_details_holder")
        h1_perfume_name = general_div.find("h1", class_="p_name_h1").contents[0]
        span_other_info = general_div.find("span", class_="p_brand_name nobold")

        # Expect 2 a hrefs (one for brand name, one for release year)
        a_tags = span_other_info.find_all("a")
        a_brand_name = a_tags[0].get_text()
        a_brand_year = int(a_tags[1].get_text())

        data_dic['Name'] = h1_perfume_name
        data_dic['Brand'] = a_brand_name
        data_dic['Year'] = a_brand_year

        return data_dic

    def scrape(self):
        pg_hook = PostgresHook(postgres_conn_id='dag_connection')
        connection = pg_hook.get_conn()
        cursor = connection.cursor()

        try:
            select_query = """
                        SELECT id, link 
                        FROM etl_backlog
                        WHERE attempts < 3
                        ORDER BY id
                        LIMIT 5
                        FOR UPDATE SKIP LOCKED;
                    """
            cursor.execute(select_query)
            links = cursor.fetchall()

            if not links:
                #logging.info("No links to process.")
                print("No links to process")
                return

            total_record_list = []
            successful_link_scrape_ids = []

            for index, record in enumerate(links):
                record_id, link = record

                # Mark that we have attempted to scrape this specific link
                update_query = """
                                    UPDATE etl_backlog
                                    SET attempts = attempts + 1
                                    WHERE id = %s;
                                """
                cursor.execute(update_query, (record_id,))
                connection.commit()

                try:
                    soup = self.create_soup(link, index)
                    data_dictionary = {}
                    self.extract_general(soup, data_dictionary)
                    self.extract_notes(soup, data_dictionary)
                    self.extract_chart_items(soup, data_dictionary)
                    self.extract_rating_items(soup, data_dictionary)
                    total_record_list.append((link, data_dictionary['Name'], data_dictionary['Brand'],
                                              data_dictionary['Year'], data_dictionary['Year'], data_dictionary['Notes'],
                                              data_dictionary['Chart Categories'], data_dictionary['Chart Numbers'],
                                              data_dictionary['Scent'], data_dictionary['Longevity'], data_dictionary['Sillage'],
                                              data_dictionary['Bottle'], data_dictionary['Value For Money'],))
                    successful_link_scrape_ids.append((record_id,))
                except Exception as e:
                    print(f"Encountered an error while scraping individual link: {e}")

            # After loop, insert newly acquired data into the etl_perfume table (contains all info)
            insert_query = """
                            INSERT INTO etl_perfume (link, name, brand, rel_year, rel_decade, notes, chart_categories, 
                            chart_numbers, scent, longevity, sillage, bottle, value_for_money)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                            """

            cursor.executemany(insert_query, total_record_list)

            # Delete the entries from the backlog that have been successfully scraped (no need to scrape again)
            delete_query = """
                            DELETE FROM etl_backlog
                            WHERE etl_backlog.id = %s
                            """

            cursor.executemany(delete_query, successful_link_scrape_ids)
            connection.commit()

        except Exception as e:
            connection.rollback()
            logging.error(f"Error processing individual link extraction, possibly SQL related: {e}")
        finally:
            cursor.close()
            connection.close()
            self.driver_instance.stop_driver()
            return


def extract():
    driver = ScrapeDriver()
    scraper = Scraper(driver)
    return scraper.scrape()
