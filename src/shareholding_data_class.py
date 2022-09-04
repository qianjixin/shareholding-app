import pandas as pd
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sqlite3
from utils import *
from config import *

logger = logging.getLogger(__name__)

class ShareholdingData:

    @staticmethod
    def timestamp_to_date_str(timestamp: pd.Timestmap) -> str:
        return timestamp.strftime('%Y/%m/%d')

    @classmethod
    def date_stock_code_exists_in_db(cls, date: pd.Timestamp, stock_code: int) -> bool:
        # Function to return whether the data for the date, stock_code combination already exists in the shareholding table
        date_str = cls.timestamp_to_date_str(date)
        with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as conn:
            query = f"""
            SELECT 1 from {SHAREHOLDING_TABLE_NAME}
            WHERE (date_str='{date_str}') AND (stock_code={stock_code}')
            LIMIT 1;
            """
            response_df = pd.read_sql(query, conn)
            return (not response_df.empty)

    @classmethod
    def scrape_table(cls, date: pd.Timestamp, stock_code: int) -> pd.DataFrame:
        date_str = cls.timestamp_to_date_str(date)
        logger.info(f'Scraping data for date={date_str}, stock_code={stock_code}...')
        try:
            # Initialise Remote WebDriver with context manager
            with initialise_driver() as driver:
                driver.get(CCASS_SHAREHOLDING_SEARCH_URL)

                # Locate btnSearch element to confirm search dialog has loaded (implicit wait)
                btn_search_element = driver.find_element(By.ID, 'btnSearch')

                # Enter date field
                shareholding_date_element = driver.find_element(By.ID, 'txtShareholdingDate')
                driver.execute_script(f'document.getElementById("txtShareholdingDate").setAttribute("value", "{date_str}")')
                
                # TODO: Better date validation, because site will auto-correct to business days
                date_str_actual = shareholding_date_element.get_attribute('value')
                assert date_str == date_str_actual, 'Invalid date entered.'

                # Enter stock code field
                stock_code_element = driver.find_element(By.ID, 'txtStockCode')
                driver.execute_script(f'document.getElementById("txtStockCode").setAttribute("value", {stock_code})')

                # TODO: Better stock code validation
                stock_code_str_actual = stock_code_element.get_attribute('value')
                assert str(stock_code) == stock_code_str_actual, 'Invalid stock code entered.'

                # Click search button
                btn_search_element.click()

                # Locate pnlResultNormal (table) element to confirm table has loaded (implicit wait)
                driver.find_element(By.ID, 'pnlResultNor`mal')

                # Use bs4 to extract table as tag
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                pnl_result_normal_tag = soup.find('div', id='pnlResultNormal')

                # Remove duplicated header values from rows in table by removing tags
                mobile_list_heading_tag_list = pnl_result_normal_tag.find_all('div', class_='mobile-list-heading')
                for element in mobile_list_heading_tag_list:
                    element.decompose()
                
                # Read table from the tag as a data frame
                df = pd.read_html(str(pnl_result_normal_tag))[0]

                # TODO: Process column names

                # Append date_str and stock_code as a columns
                df['date_str'] = date_str
                df['stock_code'] = stock_code

                # Write to shareholding database table
                with sqlite3.connect(SHAREHOLDING_DATA_DB_PATH) as conn:
                    df.to_sql(
                        name=SHAREHOLDING_TABLE_NAME,
                        con=conn,
                        if_exists='append',
                        index=False
                    )
                    logger.info(f'Successfully wrote to database for date={date_str}, stock_code={stock_code}')

        except BaseException as e:
            logger.error(f'date={date}, stock_code={stock_code}, {e}')

    # TODO: Function to retrieve all shareholding data across a given date range, given a stock_code
    @classmethod
    def get_stock_shareholding_data(start_date: pd.Timestamp, end_date: pd.Timestamp, stock_code: int) -> pd.DataFrame:
        pass


if __name__ == '__main__':
    ShareholdingData.scrape_table(
        date=pd.Timestamp(year=2022, month=8, day=1),
        stock_code=10
    )

logger.info('All done.')
