import pandas as pd
import streamlit as st

@st.cache_data
def load_data(path):

    return pd.read_csv(path)