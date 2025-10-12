"""
Configuración de Firebase para autenticación Premium
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json


def initialize_firebase():
    """Inicializa Firebase (solo una vez)"""
    if not firebase_admin._apps:
        try:
            # Leer credenciales como JSON string
            firebase_creds_json = st.secrets["firebase_json"]
            
            # Parsear JSON
            import json
            cred_dict = json.loads(firebase_creds_json)
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            return True
        except Exception as e:
            st.error(f"Error inicializando Firebase: {str(e)}")
            return False
    return True


def get_firestore_client():
    """
    Obtiene el cliente de Firestore
    """
    if initialize_firebase():
        return firestore.client()
    return None


def check_premium_code(code):
    """
    Verifica si un código Premium es válido consultando Firestore
    
    Args:
        code (str): Código Premium a verificar
        
    Returns:
        tuple: (is_valid, license_info_or_error_message)
    """
    try:
        db = get_firestore_client()
        
        if db is None:
            return False, "Error de conexión con base de datos"
        
        # Limpiar el código (quitar espacios)
        code = code.strip().upper()
        
        # Buscar código en Firestore
        doc_ref = db.collection('premium_codes').document(code)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False, "Código no válido o no encontrado"
        
        license_info = doc.to_dict()
        
        # Verificar si está activo
        if not license_info.get('isActive', False):
            return False, "Código desactivado"
        
        # Verificar expiración
        expiry_str = license_info.get('expires', '')
        
        try:
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
            
            if datetime.now().date() > expiry_date:
                return False, "Código expirado"
        except Exception as e:
            return False, f"Error verificando fecha de expiración: {str(e)}"
        
        # Código válido
        return True, license_info
        
    except Exception as e:
        st.error(f"Error verificando código: {str(e)}")
        return False, f"Error de verificación: {str(e)}"


def activate_premium_code(code, session_state):
    """
    Activa un código Premium y configura la sesión del usuario
    
    Args:
        code (str): Código Premium a activar
        session_state: Objeto st.session_state
        
    Returns:
        tuple: (success, message)
    """
    is_valid, result = check_premium_code(code)
    
    if is_valid:
        # Configurar sesión como usuario Premium
        session_state.authenticated = True
        session_state.user_tier = 'premium'
        session_state.user_email = result.get('email', '')
        session_state.license_code = code
        session_state.expires = result.get('expires', '')
        session_state.customer_name = result.get('customerName', 'Usuario Premium')
        
        return True, "✅ Código Premium activado correctamente"
    else:
        return False, f"❌ {result}"


def get_license_info(code):
    """
    Obtiene información detallada de una licencia
    
    Args:
        code (str): Código Premium
        
    Returns:
        dict: Información de la licencia o None
    """
    try:
        db = get_firestore_client()
        
        if db is None:
            return None
        
        code = code.strip().upper()
        doc_ref = db.collection('premium_codes').document(code)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
        
    except Exception as e:
        st.error(f"Error obteniendo información de licencia: {str(e)}")
        return None
