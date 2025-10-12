"""
Gestor de Sesión con localStorage para persistencia mejorada
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime

def save_session_to_storage():
    """Guarda la sesión en localStorage del navegador"""
    
    user_tier = st.session_state.get('user_tier', '')
    user_email = st.session_state.get('user_email', '')
    license_code = st.session_state.get('license_code', '')
    expires = st.session_state.get('expires', '')
    customer_name = st.session_state.get('customer_name', '')
    
    # JavaScript para guardar en localStorage
    components.html(f"""
        <script>
            localStorage.setItem('excel_user_tier', '{user_tier}');
            localStorage.setItem('excel_user_email', '{user_email}');
            localStorage.setItem('excel_license_code', '{license_code}');
            localStorage.setItem('excel_expires', '{expires}');
            localStorage.setItem('excel_customer_name', '{customer_name}');
            localStorage.setItem('excel_session_timestamp', '{datetime.now().isoformat()}');
        </script>
    """, height=0)

def load_session_from_storage():
    """Intenta cargar la sesión desde localStorage"""
    
    # JavaScript para leer localStorage y pasarlo a Python
    result = components.html("""
        <script>
            const data = {
                user_tier: localStorage.getItem('excel_user_tier'),
                user_email: localStorage.getItem('excel_user_email'),
                license_code: localStorage.getItem('excel_license_code'),
                expires: localStorage.getItem('excel_expires'),
                customer_name: localStorage.getItem('excel_customer_name'),
                timestamp: localStorage.getItem('excel_session_timestamp')
            };
            
            // Enviar datos de vuelta a Streamlit
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: data}, '*');
        </script>
    """, height=0)
    
    return result

def clear_session_storage():
    """Limpia la sesión del localStorage"""
    
    components.html("""
        <script>
            localStorage.removeItem('excel_user_tier');
            localStorage.removeItem('excel_user_email');
            localStorage.removeItem('excel_license_code');
            localStorage.removeItem('excel_expires');
            localStorage.removeItem('excel_customer_name');
            localStorage.removeItem('excel_session_timestamp');
        </script>
    """, height=0)
