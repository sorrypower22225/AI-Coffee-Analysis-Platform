import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.sql_query import run_query

# =========================
# SQL 查詢
# =========================

query = """

SELECT
    store_location,
    SUM(Total_Bill) AS total_sales
FROM coffee_sales
GROUP BY store_location

"""

df = run_query(query)

print(df)