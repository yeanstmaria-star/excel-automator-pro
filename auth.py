"""
Sistema de Autenticación y Licencias - Excel Automator Pro
Versión: 2.5 - Funcional con persistencia por URL
"""

import streamlit as st
from datetime import datetime

# LÍMITES POR TIER
TIER_LIMITS = {
    'free': {
        'daily_analyses': 3,
        'max_file_size_mb': 5,
        'features': ['básico', 'gráficos_simples'],
        'name': '🆓 Gratis'
    },
    'premium': {
        'daily_analyses': 999999,
        'max_file_size_mb': 50,
        'features': ['básico', 'gráficos_simples', 'gráficos_avanzados', 'exportar_pdf'],
        'name': '💎 Premium'
    }
}

def initialize_session():
    """Inicializa variables de sesión"""
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
    if 'show_account_page' not in st.session_state:
        st.session_state.show_account_page = False
    if 'session_restored' not in st.session_state:
        st.session_state.session_restored = False

def check_code_validity(code):
    """Verifica código Premium"""
    try:
        import firebase_config
        return firebase_config.check_premium_code(code)
    except Exception as e:
        return False, str(e)

def reset_daily_counter():
    """Resetea contador diario"""
    today = datetime.now().date()
    if st.session_state.last_reset != today:
        st.session_state.daily_uses = 0
        st.session_state.last_reset = today

def increment_usage():
    """Incrementa usos diarios"""
    st.session_state.daily_uses += 1

def check_usage_limit():
    """Verifica límite de uso"""
    reset_daily_counter()
    if st.session_state.user_tier == 'premium':
        return True, None
    limit = TIER_LIMITS['free']['daily_analyses']
    current = st.session_state.daily_uses
    if current >= limit:
        return False, f"Has alcanzado el límite diario ({limit} análisis)"
    return True, None

def show_my_account_page():
    """Página Mi Cuenta"""
    st.markdown('<h1 style="text-align: center;">💎 Mi Cuenta Premium</h1>', unsafe_allow_html=True)
    
    if st.session_state.user_tier != 'premium':
        st.warning("⚠️ Solo para usuarios Premium")
        if st.button("← Volver"):
            st.session_state.show_account_page = False
            st.rerun()
        return
    
    st.success("✨ MIEMBRO PREMIUM ACTIVO")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Nombre:**")
        st.info(f"👨‍💼 {st.session_state.get('customer_name', 'Usuario Premium')}")
    with col2:
        st.write("**Email:**")
        st.info(f"📧 {st.session_state.get('user_email', 'No disponible')}")
    
    st.markdown("---")
    st.subheader("🔑 Licencia")
    
    if st.session_state.get('license_code'):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Código:**")
            st.code(st.session_state.license_code)
        with col2:
            st.write("**Válida hasta:**")
            st.info(f"📅 {st.session_state.get('expires', 'N/A')}")
    
    st.markdown("---")
    st.subheader("📊 Plan Premium")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Análisis", "ILIMITADOS")
    with col2:
        st.metric("Archivos", "50 MB")
    with col3:
        st.metric("Funciones", "TODAS")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Renovar", use_container_width=True):
            st.markdown('[💳 Renovar Premium](https://smartappslab.gumroad.com/l/owmzol)')
    with col2:
        if st.button("📧 Soporte", use_container_width=True):
            st.info("support@excelautomatorpro.com")
    with col3:
        if st.button("🎁 Compartir", use_container_width=True):
            st.info("https://smartappslab.gumroad.com/l/owmzol")
    
    st.markdown("---")
    if st.button("← Volver a la App", use_container_width=True):
        st.session_state.show_account_page = False
        st.rerun()

def show_auth_screen():
    """Pantalla de login"""
    st.markdown('<h1 style="text-align: center;">📊 Excel Automator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Automatiza tu análisis de datos</p>', unsafe_allow_html=True)
    
    st.info("👋 ¡Bienvenido! Elige tu plan para comenzar:")
    
    tab1, tab2 = st.tabs(["🆓 Plan Gratuito", "💎 Plan Premium"])
    
    with tab1:
        st.subheader("Plan Gratuito")
        st.write("✅ 3 análisis por día")
        st.write("✅ Archivos hasta 5 MB")
        st.write("✅ Gráficos básicos")
        st.write("✅ Limpieza de datos")
        
        if st.button("🚀 Comenzar Gratis", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_tier = 'free'
            st.rerun()
    
    with tab2:
        st.subheader("Plan Premium")
        st.write("✅ Análisis ILIMITADOS")
        st.write("✅ Archivos hasta 50 MB")
        st.write("✅ Todos los gráficos")
        st.write("✅ Exportar PDF")
        st.write("✅ Sin marca de agua")
        
        st.markdown("""
        <a href="https://smartappslab.gumroad.com/l/owmzol" target="_blank">
            <button style="
                background: #ffa500;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
                width: 100%;
                cursor: pointer;
            ">💳 Comprar Premium</button>
        </a>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.write("**¿Ya compraste Premium?**")
        
        code = st.text_input("Código de Activación", placeholder="PREMIUM-XXXX-XXXX", key="code_input")
        
        if st.button("🔓 Activar", type="primary", key="activate_btn"):
            if code:
                with st.spinner("Verificando código..."):
                    is_valid, result = check_code_validity(code)
                
                if is_valid:
                    st.session_state.authenticated = True
                    st.session_state.user_tier = 'premium'
                    st.session_state.user_email = result.get('email', '')
                    st.session_state.license_code = code
                    st.session_state.expires = result.get('expires', '')
                    st.session_state.customer_name = result.get('customerName', 'Usuario Premium')
                    
                    st.success("✅ ¡Código Premium activado!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error(f"❌ {result}")
            else:
                st.warning("⚠️ Ingresa un código")

def show_user_info_sidebar():
    """Sidebar con info del usuario"""
    st.sidebar.info("📱 **En móvil:** Busca el botón ☰ arriba a la izquierda")
    st.sidebar.markdown("---")
    
    tier_name = TIER_LIMITS[st.session_state.user_tier]['name']
    st.sidebar.subheader(tier_name)
    
    if st.session_state.user_tier == 'free':
        reset_daily_counter()
        remaining = TIER_LIMITS['free']['daily_analyses'] - st.session_state.daily_uses
        st.sidebar.metric("Análisis hoy", f"{remaining}/3")
        progress = st.session_state.daily_uses / 3
        st.sidebar.progress(progress)
        
        if remaining <= 1:
            st.sidebar.warning("⚠️ Casi sin usos")
        
        st.sidebar.markdown("---")
        st.sidebar.info("💎 **Actualiza a Premium**\n\n✅ Análisis ilimitados\n✅ Todas las funciones")
        
        if st.sidebar.button("🚀 Ver Premium", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    else:
        st.sidebar.success("✅ Premium Activo")
        st.sidebar.write("🚀 Análisis ilimitados")
        
        if st.session_state.customer_name:
            st.sidebar.write(f"👤 {st.session_state.customer_name}")
        if st.session_state.user_email:
            st.sidebar.write(f"📧 {st.session_state.user_email}")
        if st.session_state.expires:
            st.sidebar.write(f"📅 Válido hasta: {st.session_state.expires}")
        
        st.sidebar.markdown("---")
        
        if st.sidebar.button("👤 Mi Cuenta", type="primary", use_container_width=True):
            st.session_state.show_account_page = True
            st.rerun()
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def require_auth():
    """Función principal de autenticación"""
    initialize_session()
    
    if not st.session_state.authenticated:
        show_auth_screen()
        return False
    
    show_user_info_sidebar()
    return True
