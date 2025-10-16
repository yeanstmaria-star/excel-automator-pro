import streamlit as st

st.set_page_config(
    page_title="TEST",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("SIDEBAR DE PRUEBA")
st.sidebar.write("Si ves esto, el sidebar funciona")

st.title("PÁGINA PRINCIPAL")
st.write("Si ves esto, la página funciona")

st.info("TEST: ¿Ves el sidebar a la izquierda?")
