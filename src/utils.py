from selenium import webdriver
from config import *

def initialise_driver():
    # Initialises a remote Chrome webdriver session
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--start-maximized')
    if HEADLESS:
        options.add_argument('--headless')
    driver = webdriver.Remote(command_executor=REMOTE_WEBDRIVER_COMMAND_EXECUTOR_URL, options=options)
    driver.implicitly_wait(IMPLICIT_WAIT_SECONDS)
    return driver
