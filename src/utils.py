import selenium
from selenium import webdriver
import sqlite3
from queries import *
from config import *

def initialise_driver() -> selenium.webdriver:
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
    driver.get(CCASS_SHAREHOLDING_SEARCH_URL)
    return driver


def initialise_shareholding_db():
    # 1. Initialise shareholding table
    with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as con:
        cur = con.cursor()
        cur.execute(CREATE_SHAREHOLDING_TABLE_QUERY)


def get_table_type(df_column: pd.Series) -> str:
    # Get column type for Dash DataTable
    if isinstance(df_column.dtype, pd.DatetimeTZDtype):
        return 'datetime',
    elif (isinstance(df_column.dtype, pd.StringDtype) or
            isinstance(df_column.dtype, pd.BooleanDtype) or
            isinstance(df_column.dtype, pd.CategoricalDtype) or
            isinstance(df_column.dtype, pd.PeriodDtype)):
        return 'text'
    elif (isinstance(df_column.dtype, pd.SparseDtype) or
            isinstance(df_column.dtype, pd.IntervalDtype) or
            isinstance(df_column.dtype, pd.Int8Dtype) or
            isinstance(df_column.dtype, pd.Int16Dtype) or
            isinstance(df_column.dtype, pd.Int32Dtype) or
            isinstance(df_column.dtype, pd.Int64Dtype)):
        return 'numeric'
    else:
        return 'any'
