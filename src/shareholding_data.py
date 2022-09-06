import pandas as pd
import selenium
from selenium.webdriver.common.by import By
from selenium.common.exceptions import UnexpectedAlertPresentException
from bs4 import BeautifulSoup
import sqlite3

from utils import *
from config import *
from queries import *


logger = logging.getLogger(__name__)


class ShareholdingData:
    """ Web scraper for the CCASS shareholding search page. 
    
    Uses a local SQLite database to store and retrieve the scraped data.

    """
    # Initialise the shareholding database and table
    initialise_shareholding_db()

    # Initialise ephemeral list to store unavailable stock_code values to speed up scraper
    # Not stored permanently because new stock codes may be created in the future
    unavailable_stock_codes = []

    @staticmethod
    def _check_date_stock_data_exists_in_db(date: pd.Timestamp, stock_code: int) -> bool:
        """ For a single (date, stock_code) combination, checks the local database whether the relevant data has already been scraped.

        Args:
            date (pd.Timestamp): Shareholding date.
            stock_code (int): HKEX stock code.

        Returns:
            bool: True when the requested data exists in the database, False otherwise.

        """
        # Returns True when the requested date and stock_code already exist in the DB
        with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as con:
            response_df = pd.read_sql(
                sql=CHECK_DATE_STOCK_DATA_IN_DB_QUERY.format(
                    date_requested=date.strftime(DATE_BASE_FORMAT),
                    stock_code=stock_code
                ),
                con=con
            )
        return not response_df.empty

    @staticmethod
    def _check_date_range_stock_data_exists_in_db(start_date: pd.Timestamp, end_date: pd.Timestamp, stock_code: int) -> pd.Series:
        """ For a given stock_code, checks the local database whether the relevant data for a date range has already been scraped.

        Args:
            start_date (pd.Timestamp): Start of the date range.
            end_date (pd.Timestamp): End of the date range.
            stock_code (int): HKEX stock code.

        Returns:
            pd.Series: True on the indices where the data exists, False otherwise.

        """
        # For a given date_range and stock_code, returns whether each date already exists in the DB
        with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as con:
            response_df = pd.read_sql(
                sql=CHECK_DATE_RANGE_STOCK_DATA_IN_DB_QUERY.format(
                    stock_code=stock_code
                ),
                con=con
            )
        return pd.Series(pd.date_range(start=start_date, end=end_date)).isin(response_df['date_requested'])

    @classmethod
    def _scrape_date_stock_data(cls, date: pd.Timestamp, stock_code: int, driver: selenium.webdriver, check_if_exists_in_db: bool = False) -> None:
        """ Scrapes the CCASS shareholding data for a given date and stock_code. Stores the output in the shareholding table of the SQLite database.

        Args:
            date (pd.Timestamp): Shareholding date.
            stock_code (int): HKEX stock code.
            driver (selenium.webdriver): Selenium WebDriver to be used to scrape the website.
            check_if_exists_in_db (bool, optional): If True, it will skip when the relevant data already exists in the database. Defaults to False.
        """
        date_base = date.strftime(DATE_BASE_FORMAT)
        date_hkex = date.strftime(DATE_HKEX_FORMAT)

        # Checking whether to skip
        if check_if_exists_in_db and cls._check_date_stock_data_exists_in_db(date, stock_code):
            # Skip if already in DB
            logger.info(
                f'Data for date={date_base}, stock_code={stock_code} already scraped. Skipped.')
            return
        elif stock_code in cls.unavailable_stock_codes:
            # Skip is stock_code has previously been recorded as unavailable
            logger.info(
                f'date={date_base}, stock_code={stock_code} skipped because stock_code is unavailable.')
            return

        # Running scraper
        logger.info(
            f'Scraping data for date={date_base}, stock_code={stock_code}...')
        try:
            # Locate btnSearch element to confirm search dialog has loaded (implicit wait)
            btn_search_element = driver.find_element(By.ID, 'btnSearch')

            # Enter date field
            driver.execute_script(
                f'document.getElementById("txtShareholdingDate").setAttribute("value", "{date_hkex}")')

            # Enter stock code field
            driver.execute_script(
                f'document.getElementById("txtStockCode").setAttribute("value", {stock_code})')

            # Click search button
            btn_search_element.click()

            # Locate pnlResultNormal (table) element to confirm table has loaded (implicit wait)
            driver.find_element(By.ID, 'pnlResultNormal')

            # Site will auto-correct back values that are Sundays or HK public holidays
            shareholding_date_element = driver.find_element(
                By.ID, 'txtShareholdingDate')
            date_hkex_displayed = shareholding_date_element.get_attribute(
                'value')

            # Get stock_name
            stock_name = driver.find_element(
                By.ID, 'txtStockName').get_attribute('value')

            # Use bs4 to parse table
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            # Reading detailed shareholding table
            pnl_result_normal_tag = soup.find('div', id='pnlResultNormal')

            # Remove duplicated header values from rows in table by removing tags
            mobile_list_heading_tag_list = pnl_result_normal_tag.find_all(
                'div', class_='mobile-list-heading')
            for element in mobile_list_heading_tag_list:
                element.decompose()

            # Read table from the tag as a data frame
            df = pd.read_html(str(pnl_result_normal_tag))[0]

            df = df.rename(columns={
                'Participant ID': 'participant_id',
                'Name of CCASS Participant(* for Consenting Investor Participants )': 'participant_name',
                'Shareholding': 'shareholding',
                '% of the total number of Issued Shares/ Warrants/ Units': 'pct_total_issued'
            }
            )
            df = df[['participant_id', 'participant_name',
                     'shareholding', 'pct_total_issued']]

            # Convert pct_total_issued to numeric
            df['pct_total_issued'] = pd.to_numeric(
                df['pct_total_issued'].str.rstrip('%'))

            # Append date_requested, date and stock_code as a columns
            df.insert(0, 'date_requested', date_base),
            df.insert(1, 'date', pd.Timestamp(
                date_hkex_displayed).strftime(DATE_BASE_FORMAT))
            df.insert(2, 'stock_code', stock_code)
            df.insert(3, 'stock_name', stock_name)

            # Verify columns before writing to database
            assert list(df.columns) == ['date_requested', 'date', 'stock_code', 'stock_name', 'participant_id',
                                        'participant_name', 'shareholding', 'pct_total_issued'], 'Columns do not match schema'

            # Write to shareholding database table
            with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as con:
                df.to_sql(
                    name='shareholding',
                    con=con,
                    if_exists='append',
                    index=False
                )
                logger.info(
                    f'date={date_base}, stock_code={stock_code}, successfully written to database.')

        except UnexpectedAlertPresentException as e:
            logger.error(f'date={date_base}, stock_code={stock_code}, {e}')
            if 'does not exist OR not available for enquiry' in e.msg:
                cls.unavailable_stock_codes.append(stock_code)
                logger.info(
                    f'stock_code={stock_code} added to list of unavailable stock codes.')

        except BaseException as e:
            logger.error(f'date={date_base}, stock_code={stock_code}, {e}')

    @classmethod
    def pull_shareholding_data(cls, start_date: pd.Timestamp, end_date: pd.Timestamp, stock_code: int) -> pd.DataFrame:
        """ Retrieves shareholding data from the SQLite database. Runs scraper when the requested data doesn't already exist in the database.

        Args:
            start_date (pd.Timestamp): Start of the date range.
            end_date (pd.Timestamp): End of the date range.
            stock_code (int): HKEX stock code.

        Returns:
            pd.DataFrame: Table of shareholding data.
        """
        date_range = pd.date_range(start=start_date, end=end_date)

        # Check which dates in date_range already exist in DB
        date_range_check = cls._check_date_range_stock_data_exists_in_db(
            start_date, end_date, stock_code)

        # Run scraper if not all dates already available in the DB
        if not cls._check_date_range_stock_data_exists_in_db(start_date, end_date, stock_code).all():
            with initialise_driver() as driver:
                for date in date_range[~date_range_check]:
                    cls._scrape_date_stock_data(date, stock_code, driver)

        # Pull from DB as a DataFarme
        with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as con:
            response_df = pd.read_sql(
                sql=PULL_SHAREHOLDING_DATA_QUERY.format(
                    start_date=start_date.strftime(DATE_BASE_FORMAT),
                    end_date=end_date.strftime(DATE_BASE_FORMAT),
                    stock_code=stock_code
                ),
                con=con
            )
        return response_df
