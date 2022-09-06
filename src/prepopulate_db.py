from shareholding_data_class import ShareholdingData
from config import *

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    ShareholdingData.prepopulate_shareholding_db()

logger.info('All done.')
