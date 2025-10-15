"""
AUTOMATIZADOR EXCEL PROFESIONAL - VERSIÓN PREMIUM
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np
from datetime import datetime
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Excel Automator Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"  # CAMBIADO A EXPANDED
)

import auth

if not auth.require_auth():
    st.stop()

if st.session_state.get('show_account_page', False):
    auth.show_my_account_page()
    st.stop()

can_use, error_message = auth.check_usage_limit()

if not can_use:
    st.error(f"🔒 {error_message}")
    st.info("💡 **Actualiza a Premium** para análisis ilimitados")
    st.markdown("""
    ### ¿Por qué Premium?
    ✅ **Análisis ilimitados**
    ✅ **Archivos más grandes**
    ✅ **Funciones avanzadas**
    [💳 Ver Planes](https://smartappslab.gumroad.com/l/owmzol)
    """)
    st.stop()

# =====================================================================
# CSS CON SIDEBAR SIEMPRE DISPONIBLE EN MÓVIL
# =====================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { padding: 2rem; background-color: #f7fafc; }
    
    h1 {
        color: #1a202c;
        text-align: center;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    
    /* SIDEBAR SIEMPRE EN EL DOM */
    [data-testid="stSidebar"] {
        background-color: #2d3748 !important;
        position: fixed !important;
        left: 0 !important;
        top: 0 !important;
        height: 100vh !important;
        z-index: 999998 !important;
        transition: transform 0.3s ease !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-100%) !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="true"] {
        transform: translateX(0) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* OCULTAR HEADER */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    #MainMenu,
    footer {
        display: none !important;
    }
    
    /* OVERLAY OSCURO */
    #sidebar-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999997;
    }
    
    #sidebar-overlay.active {
        display: block;
    }
    
    /* BOTÓN FLOTANTE */
    #menu-toggle {
        position: fixed;
        bottom: 24px;
        right: 24px;
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #10b981, #14b8a6);
        border: 3px solid white;
        border-radius: 50%;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.6);
        display: none;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 999999;
        animation: pulse 2s infinite;
    }
    
    #menu-toggle svg {
        width: 36px;
        height: 36px;
    }
    
    #menu-toggle::before {
        content: "MENÚ";
        position: absolute;
        bottom: 100%;
        margin-bottom: 8px;
        background: rgba(16, 185, 129, 0.95);
        color: white;
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    @media (max-width: 768px) {
        #menu-toggle { display: flex !important; }
        
        /* Sidebar comienza cerrado en móvil */
        [data-testid="stSidebar"] {
            transform: translateX(-100%) !important;
        }
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #14b8a6, #10b981);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
    }
</style>

<div id="sidebar-overlay"></div>

<div id="menu-toggle">
    <svg viewBox="0 0 24 24" fill="none">
        <path d="M3 12h18M3 6h18M3 18h18" stroke="white" stroke-width="3" stroke-linecap="round"/>
    </svg>
</div>

<script>
(function() {
    var sidebarOpen = false;
    
    function toggleSidebar() {
        var sidebar = document.querySelector('section[data-testid="stSidebar"]');
        var overlay = document.getElementById('sidebar-overlay');
        
        if (!sidebar) {
            console.error('Sidebar no encontrado en el DOM');
            
            // FALLBACK: Intentar hacer clic en el botón nativo
            var nativeBtn = document.querySelector('button[kind="header"]');
            if (nativeBtn) {
                console.log('Usando botón nativo de Streamlit');
                nativeBtn.click();
                return;
            }
            
            alert('Error: No se puede abrir el menú. Recarga la página.');
            return;
        }
        
        sidebarOpen = !sidebarOpen;
        
        if (sidebarOpen) {
            sidebar.setAttribute('aria-expanded', 'true');
            sidebar.style.transform = 'translateX(0)';
            overlay.classList.add('active');
        } else {
            sidebar.setAttribute('aria-expanded', 'false');
            sidebar.style.transform = 'translateX(-100%)';
            overlay.classList.remove('active');
        }
    }
    
    // Configurar botón
    var btn = document.getElementById('menu-toggle');
    if (btn) {
        btn.onclick = toggleSidebar;
        btn.ontouchstart = function(e) {
            e.preventDefault();
            toggleSidebar();
        };
    }
    
    // Configurar overlay (cerrar al tocar)
    var overlay = document.getElementById('sidebar-overlay');
    if (overlay) {
        overlay.onclick = toggleSidebar;
    }
    
    // Ocultar header
    setInterval(function() {
        var headers = document.querySelectorAll('[data-testid="stHeader"], [data-testid="stToolbar"]');
        headers.forEach(function(h) { if (h) h.remove(); });
    }, 500);
    
    // Asegurar sidebar en el DOM
    setTimeout(function() {
        var sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            console.log('✅ Sidebar encontrado en el DOM');
            if (window.innerWidth <= 768) {
                sidebar.setAttribute('aria-expanded', 'false');
                sidebar.style.transform = 'translateX(-100%)';
            }
        } else {
            console.error('❌ Sidebar NO encontrado después de 2 segundos');
        }
    }, 2000);
})();
</script>
""", unsafe_allow_html=True)

# =====================================================================
# FUNCIONES
# =====================================================================

def detect_outliers(df, column):
    if pd.api.types.is_numeric_dtype(df[column]):
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = df[(df[column] < lower) | (df[column] > upper)]
        return outliers, lower, upper
    return None, None, None

def generate_insights(df):
    insights = []
    null_cols = df.columns[df.isnull().any()].tolist()
    if null_cols:
        insights.append(f"⚠️ {len(null_cols)} columnas con valores faltantes")
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        insights.append(f"🔄 {dup_count} filas duplicadas ({(dup_count/len(df)*100):.1f}%)")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols[:2]:
        outliers, _, _ = detect_outliers(df, col)
        if outliers is not None and len(outliers) > 0:
            insights.append(f"📊 '{col}': {len(outliers)} outliers detectados")
    return insights if insights else ["✅ Datos sin problemas significativos"]

def create_excel_download(df, include_stats=False):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Datos', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Datos']
        header_format = workbook.add_format({'bold': True, 'bg_color': '#3b82f6', 'font_color': 'white', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            max_len = max(df[value].astype(str).apply(len).max(), len(str(value)))
            worksheet.set_column(col_num, col_num, min(max_len + 2, 50))
        if include_stats:
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 0:
                numeric_df.describe().to_excel(writer, sheet_name='Estadísticas')
    return output.getvalue()

# =====================================================================
# INTERFAZ
# =====================================================================

def main():
    st.markdown("<div style='text-align: center; margin-bottom: 3rem;'><h1>📊 Excel Automator Pro</h1><p style='color: #64748b; font-size: 1.125rem;'>Analiza y procesa tus datos en segundos</p></div>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚡ Procesamiento Automático")
        st.markdown("""
        **🤖 Al cargar tu archivo:**
        ✅ Limpieza automática
        ✅ Ordenamiento cronológico
        ✅ Eliminación de duplicados
        
        **📊 Análisis Inteligente:**
        ✅ Estadísticas descriptivas
        ✅ Correlaciones automáticas
        
        **📈 Visualizaciones:**
        ✅ Gráficos profesionales
        
        **📥 Exportación:**
        ✅ Excel formateado
        ✅ CSV optimizado
        """)
        st.markdown("---")
        st.success("💡 Todo automático")
    
    uploaded_file = st.file_uploader("Arrastra tu archivo Excel o CSV aquí", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
                df.columns = df.columns.str.strip()
            else:
                df = pd.read_excel(uploaded_file)
            
            st.info("🔧 Procesando...")
            
            initial_rows = len(df)
            df = df.dropna(axis=1, how='all').dropna(how='all')
            
            date_cols = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
            if date_cols:
                try:
                    df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], errors='coerce')
                    df = df.sort_values(by=date_cols[0]).reset_index(drop=True)
                    st.success(f"✅ Ordenado por '{date_cols[0]}'")
                except:
                    pass
            
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                df = df.drop_duplicates().reset_index(drop=True)
            
            st.success(f"✅ Archivo procesado: **{uploaded_file.name}**")
            
            if st.session_state.user_tier == 'free':
                auth.increment_usage()
                st.success(f"✅ ({st.session_state.daily_uses}/3 usados hoy)")
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "🔍 Explorar", "📈 Gráficos", "💾 Exportar"])
            
            with tab1:
                st.markdown("### Resumen")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Filas", f"{len(df):,}")
                with col2:
                    st.metric("Columnas", len(df.columns))
                with col3:
                    st.metric("Duplicados Eliminados", duplicates)
                
                st.markdown("### 🧠 Insights")
                for insight in generate_insights(df):
                    st.info(insight)
                
                st.markdown("### Vista Previa")
                st.dataframe(df.head(100), use_container_width=True)
            
            with tab2:
                st.markdown("### Análisis")
                info_list = [{'Columna': col, 'Tipo': str(df[col].dtype), 'Únicos': df[col].nunique(), 'Nulos': df[col].isnull().sum()} for col in df.columns]
                st.dataframe(pd.DataFrame(info_list), use_container_width=True, hide_index=True)
            
            with tab3:
                st.markdown("### Visualizaciones")
                viz = st.selectbox("Tipo", ["Histograma", "Box Plot", "Correlación"])
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if viz == "Histograma" and numeric_cols:
                    col = st.selectbox("Columna", numeric_cols)
                    fig = px.histogram(df, x=col, color_discrete_sequence=['#8b5cf6'])
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.markdown("### Exportar")
                if st.button("🎯 Preparar", type="primary"):
                    st.session_state['export_df'] = df
                    st.success("✅ Listo")
                
                if 'export_df' in st.session_state:
                    df_exp = st.session_state['export_df']
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = df_exp.to_csv(index=False).encode('utf-8-sig')
                        st.download_button("📥 CSV", csv, f"datos_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
                    with col2:
                        excel = create_excel_download(df_exp, True)
                        st.download_button("📥 Excel", excel, f"datos_{datetime.now().strftime('%Y%m%d')}.xlsx")
        
        except Exception as e:
            st.error(f"❌ {str(e)}")
    
    else:
        st.markdown("<div style='text-align: center; padding: 60px 20px; background: white; border-radius: 16px;'><h2 style='color: #334155;'>👆 Sube un archivo</h2></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
