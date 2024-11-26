from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display
import logging

class ScrapeDriver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver, self.display = self.setup_driver()

    """ 
    Driver initialization, default settings
    
    :param self: self instance
    """
    def setup_driver(self):
        display = Display(visible=False, size=(1920, 1080))
        display.start()

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.page_load_strategy = 'eager'

        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        return driver, display

    def stop_driver(self):
        self.driver.quit()
        self.display.stop()

    def get_driver(self):
        return self.driver

    def set_driver(self, driver):
        self.driver = driver

    def get_display(self):
        return self.display

    def set_display(self, display):
        self.display = display
