from shareholding_data import ShareholdingData
from concurrent.futures import ThreadPoolExecutor
from config import *

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    if USE_MULTITHREADING:
        # Distribute stock_code to threads
        with ThreadPoolExecutor(MULTITHREADING_MAX_WORKERS) as executor:
            executor.map(
                lambda stock_code: ShareholdingData.pull_shareholding_data(
                    PREPOPULATE_START_DATE, PREPOPULATE_END_DATE, stock_code),
                PREPOPULATE_STOCK_CODE_RANGE
            )
    else:
        for stock_code in PREPOPULATE_STOCK_CODE_RANGE:
            ShareholdingData.pull_shareholding_data(
                PREPOPULATE_START_DATE, PREPOPULATE_END_DATE, stock_code)

logger.info('All done.')
