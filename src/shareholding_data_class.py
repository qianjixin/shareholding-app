from lib2to3.pytree import Base
import pandas as pd
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sqlite3
from utils import *
from config import *
from queries import *

logger = logging.getLogger(__name__)

class ShareholdingData:

    initialise_shareholding_db()

    @staticmethod
    def check_date_stock_data_exists_in_db(date: pd.Timestamp, stock_code: int):
        # Returns True when the requested date and stock_code are already in the shareholding table
        with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as con:
            response_df = pd.read_sql(
                sql=CHECK_DATE_STOCK_DATA_IN_DB_QUERY.format(
                    date_requested=date.strftime(DATE_BASE_FORMAT),
                    stock_code=stock_code
                ),
                con=con
            )
        return not response_df.empty

    @classmethod
    def scrape_date_stock_data(cls, date: pd.Timestamp, stock_code: int):
        date_base = date.strftime(DATE_BASE_FORMAT)
        date_hkex = date.strftime(DATE_HKEX_FORMAT)

        # Skip the data scraping step when the given data already exists in the DB
        if cls.check_date_stock_data_exists_in_db(date, stock_code):
            logger.info(f'Data for date={date_base}, stock_code={stock_code} already scraped. Skipped.')
            return

        logger.info(f'Scraping data for date={date_base}, stock_code={stock_code}...')
        try:
            # Initialise Remote WebDriver with context manager
            with initialise_driver() as driver:
                driver.get(CCASS_SHAREHOLDING_SEARCH_URL)

                # Locate btnSearch element to confirm search dialog has loaded (implicit wait)
                btn_search_element = driver.find_element(By.ID, 'btnSearch')

                # Enter date field
                driver.execute_script(f'document.getElementById("txtShareholdingDate").setAttribute("value", "{date_hkex}")')

                # Enter stock code field
                driver.execute_script(f'document.getElementById("txtStockCode").setAttribute("value", {stock_code})')

                # Click search button
                btn_search_element.click()

                # Site will auto-correct back values that are Sundays or HK public holidays
                shareholding_date_element = driver.find_element(By.ID, 'txtShareholdingDate')
                date_hkex_displayed = shareholding_date_element.get_attribute('value')

                # Locate pnlResultNormal (table) element to confirm table has loaded (implicit wait)
                driver.find_element(By.ID, 'pnlResultNormal')

                # Use bs4 to parse table
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                # Reading detailed shareholding table
                pnl_result_normal_tag = soup.find('div', id='pnlResultNormal')

                # Remove duplicated header values from rows in table by removing tags
                mobile_list_heading_tag_list = pnl_result_normal_tag.find_all('div', class_='mobile-list-heading')
                for element in mobile_list_heading_tag_list:
                    element.decompose()
                
                # Read table from the tag as a data frame
                df = pd.read_html(str(pnl_result_normal_tag))[0]
                df = df.rename(columns={
                        'Participant ID': 'participant_id',
                        'Name of CCASS Participant(* for Consenting Investor Participants )': 'participant_name',
                        'Address': 'address',
                        'Shareholding': 'shareholding',
                        '% of the total number of Issued Shares/ Warrants/ Units': 'pct_total_issued'
                    }
                )

                # Convert pct_total_issued to numeric
                df['pct_total_issued'] = pd.to_numeric(df['pct_total_issued'].str.rstrip('%'))

                # Append date_requested, date and stock_code as a columns
                df.insert(0, 'date_requested', date_base),
                df.insert(1, 'date', pd.Timestamp(date_hkex_displayed).strftime(DATE_BASE_FORMAT))
                df.insert(2, 'stock_code', stock_code)

                # Verify columns before writing to database
                assert list(df.columns) == ['date_requested', 'date', 'stock_code', 'participant_id', 'participant_name', 'address', 'shareholding', 'pct_total_issued']

                # Write to shareholding database table
                with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as con:
                    df.to_sql(
                        name='shareholding',
                        con=con,
                        if_exists='append',
                        index=False
                    )
                    logger.info(f'Successfully wrote to database for date={date_base}, stock_code={stock_code}')

        except BaseException as e:
            logger.error(f'date={date_base}, stock_code={stock_code}, {e}')

    @classmethod
    def pull_shareholding_data(cls, start_date: pd.Timestamp, end_date: pd.Timestamp, stock_code: int) -> pd.DataFrame:
        # Run data scraper for days which are not already in the DB
        for date in pd.date_range(start=start_date, end=end_date):
            cls.scrape_date_stock_data(date, stock_code)
        
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
    

if __name__ == '__main__':
    # Testing
    data = ShareholdingData.pull_shareholding_data(
        start_date=pd.Timestamp(year=2022, month=7, day=1),
        end_date=pd.Timestamp(year=2022, month=7, day=14),
        stock_code=5
    )

    logger.info('All done.')
