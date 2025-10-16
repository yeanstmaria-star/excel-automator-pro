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
    initial_sidebar_state="collapsed"
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
    
    [data-testid="stSidebar"] {
        background-color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] strong {
        color: #ffffff !important;
    }
    
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    #MainMenu,
    footer {
        display: none !important;
    }
    
    #sidebar-tab {
        position: fixed;
        left: 0;
        top: 120px;
        width: 50px;
        height: 120px;
        background: linear-gradient(135deg, #10b981, #14b8a6);
        border-radius: 0 12px 12px 0;
        box-shadow: 2px 0 12px rgba(16, 185, 129, 0.4);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 999999;
        transition: all 0.3s ease;
        gap: 8px;
    }
    
    #sidebar-tab:hover {
        width: 55px;
        box-shadow: 3px 0 16px rgba(16, 185, 129, 0.6);
        transform: translateX(2px);
    }
    
    #sidebar-tab:active {
        transform: translateX(4px);
        box-shadow: 4px 0 20px rgba(16, 185, 129, 0.8);
    }
    
    #sidebar-tab svg {
        width: 24px;
        height: 24px;
        transition: transform 0.3s ease;
    }
    
    #sidebar-tab:hover svg {
        transform: translateX(3px);
    }
    
    #sidebar-tab .tab-text {
        writing-mode: vertical-rl;
        text-orientation: mixed;
        color: white;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    
    #sidebar-overlay {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 999998;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    #sidebar-overlay.active {
        display: block;
        opacity: 1;
    }
    
    @media (max-width: 768px) {
        #sidebar-tab {
            top: 80px;
            width: 45px;
            height: 100px;
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
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #4a5568;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: white;
        color: #14b8a6;
        border-bottom: 3px solid #14b8a6;
        font-weight: 600;
    }
</style>

<div id="sidebar-overlay"></div>

<div id="sidebar-tab">
    <svg viewBox="0 0 24 24" fill="none">
        <path d="M9 5l7 7-7 7" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    <span class="tab-text">Menú</span>
</div>

<script>
(function() {
    console.log('Inicializando control del sidebar');
    
    var clickCount = 0;
    
    function toggleSidebar() {
        clickCount++;
        console.log('Click numero ' + clickCount + ' en pestana');
        
        var buttonSelectors = [
            'button[kind="header"]',
            'button[data-testid="collapsedControl"]',
            'section[data-testid="stSidebar"] button',
            'button[aria-label*="sidebar"]'
        ];
        
        var buttonFound = false;
        
        for (var i = 0; i < buttonSelectors.length; i++) {
            var buttons = document.querySelectorAll(buttonSelectors[i]);
            console.log('Selector ' + i + ': ' + buttons.length + ' botones');
            
            if (buttons.length > 0) {
                for (var j = 0; j < buttons.length; j++) {
                    var btn = buttons[j];
                    var isHeaderButton = btn.closest('[data-testid="stHeader"]') || 
                                        btn.closest('[data-testid="stToolbar"]');
                    
                    if (!isHeaderButton) {
                        console.log('Boton del sidebar encontrado');
                        btn.click();
                        buttonFound = true;
                        
                        setTimeout(function() {
                            if (window.innerWidth <= 768) {
                                var overlay = document.getElementById('sidebar-overlay');
                                if (overlay) {
                                    overlay.classList.add('active');
                                }
                            }
                        }, 100);
                        
                        return;
                    }
                }
            }
        }
        
        if (!buttonFound) {
            console.error('No se encontro boton del sidebar');
            var sidebar = document.querySelector('section[data-testid="stSidebar"]');
            if (sidebar) {
                console.log('Sidebar encontrado, cambiando atributos');
                var isCollapsed = sidebar.getAttribute('aria-expanded') === 'false';
                
                if (isCollapsed) {
                    sidebar.setAttribute('aria-expanded', 'true');
                    sidebar.style.marginLeft = '0';
                    sidebar.style.transform = 'translateX(0)';
                } else {
                    sidebar.setAttribute('aria-expanded', 'false');
                    sidebar.style.marginLeft = '-21rem';
                    sidebar.style.transform = 'translateX(-100%)';
                }
                
                buttonFound = true;
            }
        }
        
        if (!buttonFound) {
            alert('No se puede abrir el menu. Recarga la pagina (F5).');
        }
    }
    
    function closeSidebar() {
        console.log('Cerrando sidebar');
        var sidebar = document.querySelector('section[data-testid="stSidebar"]');
        if (sidebar) {
            sidebar.setAttribute('aria-expanded', 'false');
        }
        
        var overlay = document.getElementById('sidebar-overlay');
        if (overlay) {
            overlay.classList.remove('active');
        }
        
        var closeButton = document.querySelector('button[kind="header"]');
        if (closeButton) {
            closeButton.click();
        }
    }
    
    var tab = document.getElementById('sidebar-tab');
    if (tab) {
        console.log('Pestana encontrada');
        
        tab.addEventListener('click', toggleSidebar);
        
        tab.addEventListener('touchstart', function(e) {
            e.preventDefault();
            toggleSidebar();
        }, {passive: false});
        
        console.log('Eventos agregados');
    }
    
    var overlay = document.getElementById('sidebar-overlay');
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
        overlay.addEventListener('touchstart', closeSidebar);
    }
    
    setInterval(function() {
        var headers = document.querySelectorAll('[data-testid="stHeader"], [data-testid="stToolbar"]');
        headers.forEach(function(h) { if (h) h.remove(); });
    }, 500);
    
    setTimeout(function() {
        console.log('TEST despues de 2 segundos');
        var sidebar = document.querySelector('section[data-testid="stSidebar"]');
        console.log('Sidebar en DOM: ' + !!sidebar);
        
        var nativeButton = document.querySelector('button[kind="header"]');
        console.log('Boton nativo: ' + !!nativeButton);
        
        var tab = document.getElementById('sidebar-tab');
        console.log('Pestana en DOM: ' + !!tab);
    }, 2000);
    
    console.log('Sistema inicializado');
})();
</script>
""", unsafe_allow_html=True)

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

def main():
    st.markdown("<div style='text-align: center; margin-bottom: 3rem;'><h1>📊 Excel Automator Pro</h1><p style='color: #64748b; font-size: 1.125rem;'>Analiza y procesa tus datos en segundos</p></div>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### ⚡ Procesamiento Automático")
        st.markdown("""
        **🤖 Al cargar tu archivo:**
        ✅ Limpieza automática de datos
        ✅ Ordenamiento cronológico
        ✅ Eliminación de duplicados
        
        **📊 Análisis Inteligente:**
        ✅ Estadísticas descriptivas
        ✅ Correlaciones automáticas
        
        **📈 Visualizaciones:**
        ✅ Gráficos profesionales
        
        **📥 Exportación:**
        ✅ Excel y CSV optimizados
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
                df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
            else:
                df = pd.read_excel(uploaded_file)
            
            st.info("🔧 Procesando...")
            
            initial_stats = {'rows': len(df), 'cols': len(df.columns), 'duplicates': df.duplicated().sum()}
            df = df.dropna(axis=1, how='all').dropna(how='all')
            
            date_cols = []
            for col in df.columns:
                if 'fecha' in col.lower() or 'date' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        if df[col].notna().sum() > len(df) * 0.5:
                            date_cols.append(col)
                    except:
                        pass
            
            if date_cols:
                df = df.sort_values(by=date_cols[0], ascending=True).reset_index(drop=True)
                st.success(f"✅ Ordenado por '{date_cols[0]}'")
            
            duplicates_removed = df.duplicated().sum()
            if duplicates_removed > 0:
                df = df.drop_duplicates().reset_index(drop=True)
            
            final_stats = {'rows': len(df), 'cols': len(df.columns)}
            
            if initial_stats != final_stats:
                st.success("✨ Limpieza Completada")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Filas Eliminadas", initial_stats['rows'] - final_stats['rows'])
                with col2:
                    st.metric("Columnas Vacías", initial_stats['cols'] - final_stats['cols'])
                with col3:
                    st.metric("Duplicados", duplicates_removed)
                with col4:
                    st.metric("Filas Finales", final_stats['rows'])
            
            st.success(f"✅ Archivo procesado: **{uploaded_file.name}**")
            
            if st.session_state.user_tier == 'free':
                auth.increment_usage()
                st.success(f"✅ ({st.session_state.daily_uses}/3 usados hoy)")
            
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "🔍 Explorar", "📈 Gráficos", "💾 Exportar"])
            
            with tab1:
                st.markdown("### Resumen General")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Filas", f"{len(df):,}")
                with col2:
                    st.metric("Columnas", len(df.columns))
                with col3:
                    completeness = 100 - (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
                    st.metric("Completitud", f"{completeness:.1f}%")
                with col4:
                    st.metric("Duplicados", df.duplicated().sum())
                
                st.markdown("---")
                st.markdown("### 🧠 Insights")
                for insight in generate_insights(df):
                    st.info(insight)
                
                st.markdown("---")
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
                        st.download_button("📥 CSV", csv, f"datos_{datetime.now().strftime('%Y%m%d')}.csv")
                    with col2:
                        excel = create_excel_download(df_exp, True)
                        st.download_button("📥 Excel", excel, f"datos_{datetime.now().strftime('%Y%m%d')}.xlsx")
        
        except Exception as e:
            st.error(f"❌ {str(e)}")
    
    else:
        st.markdown("<div style='text-align: center; padding: 60px 20px; background: white; border-radius: 16px;'><h2 style='color: #334155;'>👆 Sube un archivo</h2></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
