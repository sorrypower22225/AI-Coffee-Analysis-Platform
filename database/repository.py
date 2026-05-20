import pandas as pd
from database.connection import get_connection


class CoffeeRepository:

    @staticmethod
    def get_sales_data():

        conn = get_connection()

        query = """
        SELECT *
        FROM coffee_sales
        """

        df = pd.read_sql_query(
            query,
            conn
        )

        conn.close()

        print("資料筆數:", len(df))
        print(df.head())

        return df