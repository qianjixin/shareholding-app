from config import *

CREATE_SHAREHOLDING_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS shareholding (
    date_requested TEXT,
    date TEXT,
    stock_code INTEGER,
    participant_id TEXT,
    address TEXT,
    shareholding INTEGER,
    pct_total_issued REAL
);
"""

CHECK_DATE_STOCK_DATA_IN_DB_QUERY = """
SELECT 1 FROM shareholding
WHERE (date_requested = '{date_requested}') AND (stock_code={stock_code})
LIMIT 1;
"""

PULL_SHAREHOLDING_DATA_QUERY = """
SELECT * FROM shareholding
WHERE date_requested >= '{start_date}'
AND date_requested <= '{end_date}'
AND stock_code = {stock_code}
ORDER BY date_requested ASC, date ASC;
"""
