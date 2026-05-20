import pandas as pd
import streamlit as st

from database.connection import (
    get_connection
)


@st.cache_data
def load_data():

    conn = get_connection()

    try:

        query = """
        SELECT *
        FROM coffee_sales
        """

        df = pd.read_sql(
            query,
            conn
        )

        return df

    except Exception as e:

        st.error(
            f"資料讀取失敗: {e}"
        )

        return pd.DataFrame()

    finally:

        conn.close()