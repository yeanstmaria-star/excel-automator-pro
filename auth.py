"""
Sistema de Autenticación y Licencias - Excel Automator Pro
Versión: 2.4 - Con persistencia real usando Firebase
"""

import streamlit as st
from datetime import datetime, timedelta

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
        'daily_analyses': 999999,
        'max_file_size_mb': 50,
        'features': ['básico', 'gráficos_simples', 'gráficos_avanzados', 'exportar_pdf'],
        'name': '💎 Premium'
    }
}

# ==========================================
# FUNCIONES DE GESTIÓN DE SESIÓN
# ==========================================

def initialize_session():
    """Inicializa las variables de sesión y restaura desde Firebase si existe token"""
    
    # Obtener token de la URL si existe
    query_params = st.query_params
    session_token = query_params.get('session', None)
    
    session_restored = False
    
    # Intentar restaurar sesión desde Firebase
    if session_token and 'authenticated' not in st.session_state:
        try:
            import firebase_config
            session_data = firebase_config.get_session_data(session_token)
            
            if session_data:
                st.session_state.authenticated = True
                st.session_state.user_tier = session_data.get('user_tier')
                st.session_state.user_email = session_data.get('user_email', '')
                st.session_state.license_code = session_data.get('license_code', '')
                st.session_state.expires = session_data.get('expires', '')
                st.session_state.customer_name = session_data.get('customer_name', '')
                st.session_state.session_token = session_token
                session_restored = True
        except Exception as e:
            pass
    
    # Inicializar variables si no existen
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
    if 'session_token' not in st.session_state:
        st.session_state.session_token = None
    if 'session_restored' not in st.session_state:
        st.session_state.session_restored = session_restored

def create_persistent_session():
    """Crea una sesión persistente en Firebase y actualiza la URL"""
    try:
        import firebase_config
        
        session_token = firebase_config.create_session_token(
            user_tier=st.session_state.user_tier,
            user_email=st.session_state.get('user_email', ''),
            license_code=st.session_state.get('license_code', ''),
            expires=st.session_state.get('expires', ''),
            customer_name=st.session_state.get('customer_name', '')
        )
        
        if session_token:
            st.session_state.session_token = session_token
            # Actualizar URL con el token
            st.query_params['session'] = session_token
            return True
        return False
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        return False

def delete_persistent_session():
    """Elimina la sesión persistente de Firebase"""
    try:
        if st.session_state.get('session_token'):
            import firebase_config
            firebase_config.delete_session_token(st.session_state.session_token)
            # Limpiar query params
            if 'session' in st.query_params:
                del st.query_params['session']
    except Exception as e:
        pass

def reset_daily_counter():
    """Resetea el contador diario si es un nuevo día"""
    today = datetime.now().date()
    if st.session_state.last_reset != today:
        st.session_state.daily_uses = 0
        st.session_state.last_reset = today

def check_code_validity(code):
    """Verifica si un código es válido usando Firebase"""
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
        return True, None
    limit = TIER_LIMITS['free']['daily_analyses']
    current = st.session_state.daily_uses
    if current >= limit:
        return False, f"Has alcanzado el límite diario ({limit} análisis)"
    return True, None

# ==========================================
# PÁGINA MI CUENTA
# ==========================================

def show_my_account_page():
    """Muestra la página completa de Mi Cuenta para usuarios Premium"""
    
    st.markdown("""
    <style>
    .account-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
        text-align: center;
    }
    .premium-badge {
        background: linear-gradient(135deg, #ffa500, #ff6b35);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
        margin: 1rem 0;
    }
    .status-active {
        color: #00c853;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-warning {
        color: #ffa500;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .status-expired {
        color: #ff5252;
        font-weight: bold;
        font-size: 1.2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<p class="account-header">💎 Mi Cuenta Premium</p>', unsafe_allow_html=True)
    
    if st.session_state.user_tier != 'premium':
        st.warning("⚠️ Esta página es solo para usuarios Premium")
        if st.button("← Volver"):
            st.session_state.show_account_page = False
            st.rerun()
        return
    
    st.markdown('<div class="premium-badge">✨ MIEMBRO PREMIUM ACTIVO</div>', unsafe_allow_html=True)
    
    # INFORMACIÓN PERSONAL
    st.markdown("---")
    st.subheader("👤 Información Personal")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Nombre:**")
        customer_name = st.session_state.get('customer_name', 'Usuario Premium')
        st.info(f"👨‍💼 {customer_name}")
    with col2:
        st.markdown("**Email:**")
        user_email = st.session_state.get('user_email', 'No disponible')
        st.info(f"📧 {user_email}")
    
    # LICENCIA
    st.markdown("---")
    st.subheader("🔑 Información de Licencia")
    
    license_code = st.session_state.get('license_code', '')
    
    if license_code:
        try:
            import firebase_config
            license_info = firebase_config.get_license_info(license_code)
            
            if license_info:
                expiry_str = license_info.get('expires', '')
                try:
                    expiry_date = datetime.strptime(expiry_str, '%Y-%m-%d').date()
                    today = datetime.now().date()
                    days_remaining = (expiry_date - today).days
                    
                    if days_remaining > 30:
                        status_class = "status-active"
                        status_icon = "✅"
                        status_text = "Activa"
                    elif days_remaining > 0:
                        status_class = "status-warning"
                        status_icon = "⚠️"
                        status_text = "Por expirar pronto"
                    else:
                        status_class = "status-expired"
                        status_icon = "❌"
                        status_text = "Expirada"
                except:
                    days_remaining = None
                    status_class = "status-active"
                    status_icon = "✅"
                    status_text = "Activa"
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Código de Licencia:**")
                    st.code(license_code, language=None)
                    st.markdown("**Estado:**")
                    st.markdown(f'<p class="{status_class}">{status_icon} {status_text}</p>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown("**Válida hasta:**")
                    st.info(f"📅 {expiry_str}")
                    
                    if days_remaining is not None:
                        st.markdown("**Días restantes:**")
                        if days_remaining > 30:
                            st.success(f"⏰ {days_remaining} días")
                        elif days_remaining > 7:
                            st.warning(f"⏰ {days_remaining} días")
                        elif days_remaining > 0:
                            st.error(f"⏰ {days_remaining} días - ¡Renueva pronto!")
                        else:
                            st.error("⏰ Expirada")
                
                if days_remaining is not None and 0 < days_remaining <= 7:
                    st.warning(f"⚠️ Tu licencia expira en {days_remaining} días. Renueva ahora para mantener tu acceso Premium.")
        except Exception as e:
            st.error(f"Error cargando información de licencia: {str(e)}")
    
    # PLAN
    st.markdown("---")
    st.subheader("📊 Tu Plan Premium")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Análisis Diarios", "ILIMITADOS", delta="Sin límites")
    with col2:
        st.metric("Tamaño de Archivos", "50 MB", delta="10x más")
    with col3:
        st.metric("Funciones", "TODAS", delta="100%")
    
    st.markdown("**✨ Funciones Premium Incluidas:**")
    
    features_col1, features_col2 = st.columns(2)
    with features_col1:
        st.markdown("""
        - ✅ Análisis ilimitados
        - ✅ Gráficos avanzados
        - ✅ Exportación a PDF
        - ✅ Sin marca de agua
        """)
    with features_col2:
        st.markdown("""
        - ✅ Soporte prioritario
        - ✅ Actualizaciones gratis
        - ✅ Archivos hasta 50 MB
        - ✅ Todas las funciones futuras
        """)
    
    # ACCIONES
    st.markdown("---")
    st.subheader("🔄 Acciones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Renovar Licencia", type="primary", use_container_width=True):
            st.markdown('<meta http-equiv="refresh" content="0; url=https://smartappslab.gumroad.com/l/owmzol">', unsafe_allow_html=True)
            st.info("Redirigiendo...")
    
    with col2:
        if st.button("📧 Contactar Soporte", use_container_width=True):
            st.info("**Soporte Premium**\n\nEmail: support@excelautomatorpro.com\n\nIncluye tu código de licencia.")
    
    with col3:
        if st.button("🎁 Recomendar", use_container_width=True):
            st.info("**Comparte:**\n\nhttps://smartappslab.gumroad.com/l/owmzol")
    
    # BOTÓN VOLVER
    st.markdown("---")
    if st.button("← Volver a la App", use_container_width=True):
        st.session_state.show_account_page = False
        st.rerun()
    
    st.caption("💎 Gracias por ser un miembro Premium de Excel Automator Pro")

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
    
    st.markdown('<p class="big-title">📊 Excel Automator Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Automatiza tu análisis de datos en segundos</p>', unsafe_allow_html=True)
    
    st.info("👋 **¡Bienvenido!** Elige tu plan para comenzar:")
    
    tab1, tab2 = st.tabs(["🆓 Plan Gratuito", "💎 Plan Premium"])
    
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
                create_persistent_session()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
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
        st.subheader("¿Ya compraste Premium?")
        st.write("Ingresa tu código de licencia:")
        
        premium_code_input = st.text_input("Código de Activación", placeholder="PREMIUM-XXXX-XXXX", key="activation_code")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("🔓 Activar", key="activate_button", type="primary"):
                if premium_code_input:
                    with st.spinner("Verificando código..."):
                        is_valid, result = check_code_validity(premium_code_input)
                    
                    if is_valid:
                        st.session_state.authenticated = True
                        st.session_state.user_tier = 'premium'
                        st.session_state.user_email = result.get('email', '')
                        st.session_state.license_code = premium_code_input
                        st.session_state.expires = result.get('expires', '')
                        st.session_state.customer_name = result.get('customerName', 'Usuario Premium')
                        
                        if create_persistent_session():
                            st.success("✅ ¡Código Premium activado y sesión guardada!")
                            st.info("💾 Tu sesión persistirá incluso si cierras y abres la app")
                        else:
                            st.success("✅ ¡Código Premium activado!")
                            st.warning("⚠️ No se pudo guardar la sesión persistente")
                        
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
                else:
                    st.warning("⚠️ Por favor ingresa un código")

def show_user_info_sidebar():
    """Muestra información del usuario en el sidebar"""
    
    # Instrucciones para mobile
    st.sidebar.info("📱 **En móvil:** Busca el botón ☰ arriba a la izquierda")
    
    st.sidebar.markdown("---")
    tier_name = TIER_LIMITS[st.session_state.user_tier]['name']
    st.sidebar.subheader(f"Tu Plan: {tier_name}")
    
    # Mostrar si la sesión fue restaurada
    if st.session_state.get('session_restored', False):
        st.sidebar.success("✅ Sesión restaurada automáticamente")
    
    if st.session_state.user_tier == 'free':
        reset_daily_counter()
        remaining = TIER_LIMITS['free']['daily_analyses'] - st.session_state.daily_uses
        st.sidebar.metric("Análisis restantes hoy", f"{remaining}/3", delta=None)
        progress = st.session_state.daily_uses / TIER_LIMITS['free']['daily_analyses']
        st.sidebar.progress(progress)
        if remaining <= 1:
            st.sidebar.warning("⚠️ Casi sin usos disponibles")
        st.sidebar.markdown("---")
        st.sidebar.info("💎 **Actualiza a Premium**\n\nAnálisis ilimitados + Todas las funciones")
        if st.sidebar.button("🚀 Ver Planes Premium"):
            st.session_state.authenticated = False
            delete_persistent_session()
            st.rerun()
    else:
        st.sidebar.success("✅ Acceso Premium Activo")
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
    if st.sidebar.button("🚪 Cerrar Sesión"):
        delete_persistent_session()
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
```

**Commit ambos archivos:**
- `firebase_config.py`: "Add session token management"
- `auth.py`: "Use Firebase tokens for persistent sessions"

---

# ✅ CÓMO FUNCIONA AHORA:

1. **Usuario activa código Premium** → Se crea un token en Firebase
2. **Token se agrega a la URL** → `tu-app.streamlit.app/?session=abc123...`
3. **Usuario cierra y vuelve abrir** → El token está en la URL
4. **App lee el token de la URL** → Restaura la sesión desde Firebase
5. **✅ Sesión persiste** - Incluso en modo incógnito mientras tengas la URL

---

# 📱 PARA EL USUARIO:

**Si guarda la URL completa como marcador/favorito**, su sesión persistirá para siempre (30 días de validez del token).

**URL de ejemplo:**
```
https://tu-app.streamlit.app/?session=a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6
