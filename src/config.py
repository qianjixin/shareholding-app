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
USE_REMOTE_WEBDRIVER = True
REMOTE_WEBDRIVER_COMMAND_EXECUTOR_URL = 'http://selenium:4444/wd/hub'
HEADLESS = True
IMPLICIT_WAIT_SECONDS = 5

# Multithreading
USE_MULTITHREADING = True
MULTITHREADING_MAX_WORKERS = 2

# Constants
CCASS_SHAREHOLDING_SEARCH_URL = 'https://www3.hkexnews.hk/sdw/search/searchsdw.aspx'
DATE_HKEX_FORMAT = '%Y/%m/%d'
DATE_BASE_FORMAT = '%Y-%m-%d'

# SQLite3
SHAREHOLDING_DATA_DB_PATH = '../output/shareholding.db'

# Dash
DASH_DEBUG_MODE = True
DASH_PORT = 8888
