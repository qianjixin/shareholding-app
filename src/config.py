import logging
import sys
import pandas as pd
import numpy as np

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
USE_REMOTE_WEBDRIVER = False
REMOTE_WEBDRIVER_COMMAND_EXECUTOR_URL = 'http://selenium:4444/wd/hub'
HEADLESS = True
IMPLICIT_WAIT_SECONDS = 5

# Multithreading
USE_MULTITHREADING = True
MULTITHREADING_MAX_WORKERS = 10

# Constants
CCASS_SHAREHOLDING_SEARCH_URL = 'https://www3.hkexnews.hk/sdw/search/searchsdw.aspx'
DATE_HKEX_FORMAT = '%Y/%m/%d'
DATE_BASE_FORMAT = '%Y-%m-%d'

# SQLite3
SHAREHOLDING_DATA_DB_PATH = '../output/shareholding.db'

# Dash
DASH_DEBUG_MODE = True
DASH_PORT = 8888

# Prepoluate shareholding_db
PREPOPULATE_DB = True
PREPOPULATE_START_DATE = pd.Timestamp(year=2021, month=9, day=5)
PREPOPULATE_END_DATE = pd.Timestamp(year=2022, month=9, day=5)
PREPOLUATE_STOCK_CODE_RANGE = np.arange(1, 95500)
