import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Excel Automator Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("TEST SIDEBAR")
st.sidebar.write("¿Ves esto?")

st.title("TEST PRINCIPAL")
st.write("Si ves el sidebar a la izquierda, los imports NO son el problema")
