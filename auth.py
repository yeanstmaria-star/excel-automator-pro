"""
Sistema de Autenticación y Licencias - Excel Automator Pro
Autor: Tu nombre
Versión: 2.0 - Integrado con Firebase
"""

import streamlit as st
from datetime import datetime, timedelta
import hashlib
import firebase_config

# ==========================================
# CONFIGURACIÓN DE CÓDIGOS PREMIUM
# ==========================================

# NOTA: Los códigos ahora se leen desde Firebase/Firestore
# Este diccionario ya no se usa, pero lo dejamos comentado por referencia
"""
PREMIUM_CODES = {
    "DEMO2024-PREMIUM": {
        "expires": "2025-12-31",
        "email": "demo@test.com",
        "tier": "premium"
    },
}
"""

# ==========================================
# LÍMITES POR TIER
# ==========================================

TIER_LIMITS = {
    'free': {
        'daily_analyses': 3,
        'max_file_size_mb': 5,
        'features': ['básico', 'gráficos_simples'],
        'name': '🆓 Gratis'
    },
    'premium': {
        'daily_analyses': 999999,  # Ilimitado
        'max_file_size_mb': 50,
        'features': ['básico', 'gráficos_simples', 'gráficos_avanzados', 'exportar_pdf'],
        'name': '💎 Premium'
    }
}

# ==========================================
# FUNCIONES DE GESTIÓN DE SESIÓN
# ==========================================

def initialize_session():
    """Inicializa las variables de sesión necesarias"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_tier' not in st.session_state:
        st.session_state.user_tier = None
    
    if 'daily_uses' not in st.session_state:
        st.session_state.daily_uses = 0
    
    if 'last_reset' not in st.session_state:
        st.session_state.last_reset = datetime.now().date()
    
    if 'user_email' not in st.session_state:
        st.session_state.user_email = None
    
    if 'license_code' not in st.session_state:
        st.session_state.license_code = None
    
    if 'expires' not in st.session_state:
        st.session_state.expires = None
    
    if 'customer_name' not in st.session_state:
        st.session_state.customer_name = None

def reset_daily_counter():
    """Resetea el contador diario si es un nuevo día"""
    today = datetime.now().date()
    if st.session_state.last_reset != today:
        st.session_state.daily_uses = 0
        st.session_state.last_reset = today

def check_code_validity(code):
    """
    Verifica si un código es válido usando Firebase
    
    Returns:
        tuple: (is_valid: bool, result: dict or error_message: str)
    """
    try:
        import firebase_config
        return firebase_config.check_premium_code(code)
    except Exception as e:
        return False, f"Error al verificar código: {str(e)}"

def increment_usage():
    """Incrementa el contador de usos diarios"""
    st.session_state.daily_uses += 1

def check_usage_limit():
    """Verifica si el usuario ha alcanzado su límite diario"""
    reset_daily_counter()
    
    if st.session_state.user_tier == 'premium':
        return True, None  # Sin límites
    
    limit = TIER_LIMITS['free']['daily_analyses']
    current = st.session_state.daily_uses
    
    if current >= limit:
        return False, f"Has alcanzado el límite diario ({limit} análisis)"
    
    return True, None

# ==========================================
# INTERFAZ DE AUTENTICACIÓN
# ==========================================

def show_auth_screen():
    """Muestra la pantalla de autenticación/bienvenida"""
    
    st.markdown("""
    <style>
    .big-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .free-box {
        background-color: #f0f2f6;
        border: 2px solid #e0e0e0;
    }
    .premium-box {
        background-color: #fff4e6;
        border: 2px solid #ffa500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Título principal
    st.markdown('<p class="big-title">📊 Excel Automator Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Automatiza tu análisis de datos en segundos</p>', unsafe_allow_html=True)
    
    # Video demo o imagen (opcional)
    st.info("👋 **¡Bienvenido!** Elige tu plan para comenzar:")
    
    # Tabs para las opciones
    tab1, tab2 = st.tabs(["🆓 Plan Gratuito", "💎 Plan Premium"])
    
    # ============================================
    # TAB 1: PLAN GRATUITO
    # ============================================
    with tab1:
        st.markdown('<div class="feature-box free-box">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Plan Gratuito")
            st.write("✅ 3 análisis por día")
            st.write("✅ Archivos hasta 5 MB")
            st.write("✅ Gráficos básicos")
            st.write("✅ Limpieza de datos")
            st.write("⚠️ Marca de agua en reportes")
        
        with col2:
            st.metric("Precio", "GRATIS")
            st.write("")
            if st.button("🚀 Comenzar Gratis", key="free_button", type="primary"):
                st.session_state.authenticated = True
                st.session_state.user_tier = 'free'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ============================================
    # TAB 2: PLAN PREMIUM
    # ============================================
    with tab2:
        st.markdown('<div class="feature-box premium-box">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Plan Premium")
            st.write("✅ Análisis ILIMITADOS")
            st.write("✅ Archivos hasta 50 MB")
            st.write("✅ Todos los gráficos avanzados")
            st.write("✅ Exportar a PDF")
            st.write("✅ Sin marca de agua")
            st.write("✅ Soporte prioritario")
            st.write("✅ Actualizaciones gratis")
        
        with col2:
            st.metric("Precio", "$19.99/mes")
            st.write("")
            
            # Botón de compra - Link de Gumroad
            st.markdown("""
            <a href="https://smartappslab.gumroad.com/l/owmzol" target="_blank">
                <button style="
                    background-color: #ffa500;
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 5px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    width: 100%;
                ">
                    💳 Comprar Premium
                </button>
            </a>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.write("---")
        
        # Activación con código
        st.subheader("¿Ya compraste Premium?")
        st.write("Ingresa tu código de licencia:")
        
        premium_code_input = st.text_input(
            "Código de Activación", 
            placeholder="PREMIUM-XXXX-XXXX", 
            key="activation_code"
        )
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔓 Activar", key="activate_button", type="primary"):
                if premium_code_input:
                    # Verificar código con Firebase
                    is_valid, result = check_code_validity(premium_code_input)
                    
                    if is_valid:
                        # Activar sesión Premium
                        st.session_state.authenticated = True
                        st.session_state.user_tier = 'premium'
                        st.session_state.user_email = result.get('email', '')
                        st.session_state.license_code = premium_code_input
                        st.session_state.expires = result.get('expires', '')
                        st.session_state.customer_name = result.get('customerName', 'Usuario Premium')
                        
                        st.success("✅ ¡Código Premium activado correctamente!")
                        st.balloons()
                        st.rerun()
                    else:
                        # Mostrar error
                        st.error(f"❌ {result}")
                else:
                    st.warning("⚠️ Por favor ingresa un código")

def show_user_info_sidebar():
    """Muestra información del usuario en el sidebar"""
    st.sidebar.markdown("---")
    
    tier_name = TIER_LIMITS[st.session_state.user_tier]['name']
    st.sidebar.subheader(f"Tu Plan: {tier_name}")
    
    if st.session_state.user_tier == 'free':
        reset_daily_counter()
        remaining = TIER_LIMITS['free']['daily_analyses'] - st.session_state.daily_uses
        
        st.sidebar.metric(
            "Análisis restantes hoy",
            f"{remaining}/3",
            delta=None
        )
        
        # Barra de progreso
        progress = st.session_state.daily_uses / TIER_LIMITS['free']['daily_analyses']
        st.sidebar.progress(progress)
        
        if remaining <= 1:
            st.sidebar.warning("⚠️ Casi sin usos disponibles")
        
        st.sidebar.markdown("---")
        st.sidebar.info("💎 **Actualiza a Premium**\n\nAnálisis ilimitados + Todas las funciones")
        
        if st.sidebar.button("🚀 Ver Planes Premium"):
            st.session_state.authenticated = False
            st.rerun()
    
    else:  # Premium
        st.sidebar.success("✅ Acceso Premium Activo")
        st.sidebar.write("🚀 Análisis ilimitados")
        
        if st.session_state.customer_name:
            st.sidebar.write(f"👤 {st.session_state.customer_name}")
        
        if st.session_state.user_email:
            st.sidebar.write(f"📧 {st.session_state.user_email}")
        
        if st.session_state.expires:
            st.sidebar.write(f"📅 Válido hasta: {st.session_state.expires}")
    
    # Botón de logout
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ==========================================
# FUNCIÓN PRINCIPAL DE AUTENTICACIÓN
# ==========================================

def require_auth():
    """
    Función principal que debe llamarse al inicio de tu app.
    Retorna True si el usuario está autenticado, False si no.
    """
    initialize_session()
    
    if not st.session_state.authenticated:
        show_auth_screen()
        return False
    
    # Mostrar info del usuario en sidebar
    show_user_info_sidebar()
    
    return True
