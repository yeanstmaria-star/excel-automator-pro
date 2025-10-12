"""
Configuración de Firebase para autenticación Premium
"""

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


def initialize_firebase():
    """Inicializa Firebase (solo una vez)"""
    if not firebase_admin._apps:
        try:
            firebase_creds = st.secrets["firebase"]
            
            # Obtener private_key y limpiarla
            private_key = firebase_creds["private_key"]
            
            # Arreglar formato de la private_key
            # Reemplazar \\n con \n real si es necesario
            if "\\n" in private_key:
                private_key = private_key.replace("\\n", "\n")
            
            # Asegurar que empiece y termine correctamente
            if not private_key.startswith("-----BEGIN"):
                private_key = "-----BEGIN PRIVATE KEY-----\n" + private_key
            if not private_key.endswith("-----"):
                private_key = private_key + "\n-----END PRIVATE KEY-----"
            
            cred_dict = {
                "type": firebase_creds["type"],
                "project_id": firebase_creds["project_id"],
                "private_key_id": firebase_creds["private_key_id"],
                "private_key": private_key,
                "client_email": firebase_creds["client_email"],
                "client_id": firebase_creds["client_id"],
                "auth_uri": firebase_creds["auth_uri"],
                "token_uri": firebase_creds["token_uri"],
                "auth_provider_x509_cert_url": firebase_creds["auth_provider_x509_cert_url"],
                "client_x509_cert_url": firebase_creds["client_x509_cert_url"],
            }
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            return True
        except Exception as e:
            st.error(f"Error inicializando Firebase: {str(e)}")
            return False
    return True


def get_firestore_client():
    """Obtiene cliente de Firestore"""
    if initialize_firebase():
        return firestore.client()
    return None


def check_premium_code(code):
    """
    Verifica si un código Premium es válido
    
    Returns:
        tuple: (is_valid, license_info_or_error_message)
    """
    try:
        db = get_firestore_client()
        
        if db is None:
            return False, "Error de conexión"
        
        code = code.strip().upper()
        
        doc_ref = db.collection('premium_codes').document(code)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False, "Código no válido"
        
        license_info = doc.to_dict()
        
        if not license_info.get('isActive', False):
            return False, "Código desactivado"
        
        expiry_str = license_info.get('expires', '')
        
        try:
            expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
            
            if datetime.now().date() > expiry_date:
                return False, "Código expirado"
        except Exception:
            return False, "Error verificando expiración"
        
        return True, license_info
        
    except Exception as e:
        return False, f"Error: {str(e)}"
