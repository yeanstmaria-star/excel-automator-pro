import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Excel Automator Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.title("TEST SIDEBAR EN MAIN")
    st.sidebar.write("¿Ves esto?")
    
    st.title("TEST PRINCIPAL")
    st.write("Sidebar dentro de función main()")

if __name__ == "__main__":
    main()
