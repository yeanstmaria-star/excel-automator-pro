import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Excel Automator Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #2d3748;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("TEST SIDEBAR CON CSS")
st.sidebar.write("¿Ves esto?")

st.title("TEST PRINCIPAL")
st.write("¿El sidebar está oscuro?")
