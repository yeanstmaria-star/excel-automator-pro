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

# ==========================================
# GESTIÓN DE SESIONES PERSISTENTES
# ==========================================

import uuid
from datetime import datetime, timedelta

def create_session_token(user_tier, user_email, license_code, expires, customer_name):
    """Crea un token de sesión y lo guarda en Firebase"""
    try:
        # Generar token único
        session_token = str(uuid.uuid4())
        
        # Datos de la sesión
        session_data = {
            'user_tier': user_tier,
            'user_email': user_email,
            'license_code': license_code,
            'expires': expires,
            'customer_name': customer_name,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=30)).isoformat()  # Sesión válida 30 días
        }
        
        # Guardar en Firebase
        db = get_db()
        db.collection('sessions').document(session_token).set(session_data)
        
        return session_token
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        return None

def get_session_data(session_token):
    """Recupera los datos de sesión desde Firebase"""
    try:
        if not session_token:
            return None
        
        db = get_db()
        doc = db.collection('sessions').document(session_token).get()
        
        if not doc.exists:
            return None
        
        session_data = doc.to_dict()
        
        # Verificar si la sesión expiró
        expires_at = datetime.fromisoformat(session_data.get('expires_at', ''))
        if datetime.now() > expires_at:
            # Sesión expirada, eliminarla
            db.collection('sessions').document(session_token).delete()
            return None
        
        return session_data
    except Exception as e:
        print(f"Error getting session: {str(e)}")
        return None

def delete_session_token(session_token):
    """Elimina un token de sesión de Firebase"""
    try:
        if not session_token:
            return
        
        db = get_db()
        db.collection('sessions').document(session_token).delete()
    except Exception as e:
        print(f"Error deleting session: {str(e)}")
