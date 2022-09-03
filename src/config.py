import logging
import sys

OUTPUT_DIR_PATH = '../output'

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{OUTPUT_DIR_PATH}/output.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Selenium config
REMOTE_WEBDRIVER_COMMAND_EXECUTOR_URL = 'http://selenium:4444/wd/hub'
HEADLESS = False
IMPLICIT_WAIT_SECONDS = 10

# Constants
CCASS_SHAREHOLDING_SEARCH_URL = 'https://www3.hkexnews.hk/sdw/search/searchsdw.aspx'
