from selenium import webdriver
import sqlite3
from queries import *
from config import *

def initialise_driver():
    # Initialises a remote Chrome webdriver session
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--start-maximized')
    if HEADLESS:
        options.add_argument('--headless')

    if USE_REMOTE_WEBDRIVER:
        driver = webdriver.Remote(command_executor=REMOTE_WEBDRIVER_COMMAND_EXECUTOR_URL, options=options)
    else:
        driver = webdriver.Chrome(options=options)
        
    driver.implicitly_wait(IMPLICIT_WAIT_SECONDS)
    return driver


def initialise_shareholding_db():
    # 1. Initialise shareholding table
    with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as con:
        cur = con.cursor()
        cur.execute(CREATE_SHAREHOLDING_TABLE_QUERY)
