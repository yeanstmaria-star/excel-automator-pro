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
    ✅ **Análisis ilimitados** - Sin restricciones diarias
    ✅ **Archivos más grandes** - Hasta 50 MB
    ✅ **Funciones avanzadas** - Todos los tipos de gráficos
    [💳 Ver Planes](https://smartappslab.gumroad.com/l/owmzol)
    """)
    st.stop()

# =====================================================================
# CSS + BOTÓN FLOTANTE ULTRA SIMPLE
# =====================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --sidebar-bg: #2d3748;
        --sidebar-text: #e2e8f0;
        --main-bg: #f7fafc;
        --text-primary: #1a202c;
        --text-secondary: #4a5568;
        --accent-color: #14b8a6;
        --success-color: #10b981;
        --border-color: #e2e8f0;
        --shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    * { font-family: 'Inter', sans-serif; }
    
    .main {
        padding: 2rem;
        background-color: var(--main-bg);
    }
    
    h1 {
        color: var(--text-primary);
        text-align: center;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        transition: all 0.3s ease-in-out !important;
    }
    
    [data-testid="stSidebar"] * {
        color: var(--sidebar-text) !important;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--accent-color), var(--success-color));
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
    }
    
    #MainMenu, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
    }
    
    /* BOTÓN FLOTANTE */
    #menu-btn {
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
        animation: float 2s ease-in-out infinite;
    }
    
    #menu-btn svg {
        width: 36px;
        height: 36px;
    }
    
    #menu-btn::before {
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
    
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    @media (max-width: 768px) {
        #menu-btn { display: flex !important; }
    }
</style>

<div id="menu-btn" onclick="openSidebar()">
    <svg viewBox="0 0 24 24" fill="none">
        <path d="M3 12h18M3 6h18M3 18h18" stroke="white" stroke-width="3" stroke-linecap="round"/>
    </svg>
</div>

<script>
function openSidebar() {
    var s = document.querySelector('section[data-testid="stSidebar"]');
    if (s) {
        s.style.marginLeft = '0';
        s.style.transform = 'translateX(0)';
        s.style.visibility = 'visible';
        s.style.opacity = '1';
    }
}

setInterval(function() {
    var h = document.querySelectorAll('[data-testid="stHeader"], [data-testid="stToolbar"]');
    h.forEach(function(el) { if (el) el.remove(); });
}, 500);
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
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#3b82f6',
            'font_color': 'white',
            'border': 1
        })
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
    st.markdown("""
        <div style='text-align: center; margin-bottom: 3rem;'>
            <h1>📊 Excel Automator Pro</h1>
            <p style='color: #64748b; font-size: 1.125rem;'>
                Analiza y procesa tus datos en segundos
            </p>
        </div>
    """, unsafe_allow_html=True)
    
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
        ✅ Múltiples gráficos profesionales
        
        **📥 Exportación Premium:**
        ✅ Excel formateado
        ✅ CSV optimizado
        """)
        st.markdown("---")
        st.success("💡 Todo automático e inteligente")
    
    uploaded_file = st.file_uploader(
        "Arrastra tu archivo Excel o CSV aquí",
        type=['xlsx', 'xls', 'csv'],
        help="Formatos: .xlsx, .xls, .csv"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
                except:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
                    except:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, encoding='utf-8')
                df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
            else:
                df = pd.read_excel(uploaded_file)
            
            st.info("🔧 Procesando datos...")
            
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
            
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
            
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
                st.success(f"✅ Análisis completado! ({st.session_state.daily_uses}/3 usados hoy)")
            
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
                st.markdown("### 🧠 Insights Automáticos")
                for insight in generate_insights(df):
                    st.info(insight)
                
                st.markdown("---")
                st.markdown("### Vista Previa")
                search = st.text_input("🔍 Buscar", placeholder="Escribe para buscar...")
                if search:
                    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
                    filtered = df[mask]
                    st.caption(f"Mostrando {len(filtered)} resultados")
                    st.dataframe(filtered.head(50), use_container_width=True)
                else:
                    st.dataframe(df.head(100), use_container_width=True)
            
            with tab2:
                st.markdown("### Análisis Exploratorio")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Información de Columnas")
                    info_list = []
                    for col in df.columns:
                        info_list.append({
                            'Columna': col,
                            'Tipo': str(df[col].dtype),
                            'Únicos': df[col].nunique(),
                            'Nulos': df[col].isnull().sum(),
                            '% Nulos': f"{(df[col].isnull().sum() / len(df) * 100):.1f}%"
                        })
                    st.dataframe(pd.DataFrame(info_list), use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("#### Estadísticas")
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    if numeric_cols:
                        selected = st.selectbox("Selecciona columna", numeric_cols, key="explore_col")
                        col_data = df[selected].dropna()
                        st.metric("Promedio", f"{col_data.mean():.2f}")
                        st.metric("Mediana", f"{col_data.median():.2f}")
                        st.metric("Desv. Estándar", f"{col_data.std():.2f}")
                        outliers, _, _ = detect_outliers(df, selected)
                        if outliers is not None and len(outliers) > 0:
                            st.warning(f"⚠️ {len(outliers)} outliers")
                    else:
                        st.info("No hay columnas numéricas")
            
            with tab3:
                st.markdown("### Visualizaciones")
                viz_type = st.selectbox("Tipo de gráfico", ["Histograma", "Box Plot", "Scatter Plot", "Correlación", "Pie Chart"])
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if viz_type == "Histograma" and numeric_cols:
                    col = st.selectbox("Columna", numeric_cols, key="hist")
                    bins = st.slider("Bins", 10, 100, 30, key="bins")
                    fig = px.histogram(df, x=col, nbins=bins, color_discrete_sequence=['#8b5cf6'])
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Box Plot" and numeric_cols:
                    col = st.selectbox("Columna", numeric_cols, key="box")
                    fig = px.box(df, y=col, color_discrete_sequence=['#10b981'])
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Scatter Plot" and len(numeric_cols) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        x = st.selectbox("Eje X", numeric_cols, key="x")
                    with col2:
                        y = st.selectbox("Eje Y", numeric_cols, index=1 if len(numeric_cols) > 1 else 0, key="y")
                    fig = px.scatter(df, x=x, y=y, trendline="ols", color_discrete_sequence=['#f59e0b'])
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Correlación" and len(numeric_cols) >= 2:
                    corr = df[numeric_cols].corr()
                    fig = px.imshow(corr, text_auto='.2f', aspect="auto", color_continuous_scale='RdBu_r')
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Pie Chart":
                    text_cols = df.select_dtypes(include=['object']).columns.tolist()
                    if text_cols:
                        col = st.selectbox("Columna", text_cols, key="pie")
                        top = st.slider("Top N", 3, 15, 8, key="top")
                        values = df[col].value_counts().head(top)
                        fig = px.pie(values=values.values, names=values.index, hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.markdown("### Exportar Datos Procesados")
                st.info("💡 Datos ya limpiados automáticamente")
                
                col1, col2 = st.columns(2)
                with col1:
                    remove_nulls = st.checkbox("Eliminar filas con valores nulos", value=False)
                    include_stats = st.checkbox("Incluir estadísticas", value=True)
                
                if st.button("🎯 Preparar Descarga", type="primary"):
                    df_export = df.copy()
                    if remove_nulls:
                        df_export = df_export.dropna()
                    st.success("✅ Datos listos para exportar")
                    st.session_state['export_df'] = df_export
                
                st.markdown("---")
                
                if 'export_df' in st.session_state:
                    df_to_export = st.session_state['export_df']
                    st.markdown("#### 📥 Descargar")
                    col1, col2 = st.columns(2)
                    with col1:
                        csv_data = df_to_export.to_csv(index=False).encode('utf-8-sig')
                        st.download_button("📥 Descargar CSV", data=csv_data, file_name=f"datos_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")
                    with col2:
                        excel_data = create_excel_download(df_to_export, include_stats)
                        st.download_button("📥 Descargar Excel", data=excel_data, file_name=f"datos_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    st.markdown("#### 👀 Vista Previa")
                    st.dataframe(df_to_export.head(20), use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Verifica el formato del archivo")
    
    else:
        st.markdown("""
            <div style='text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <h2 style='color: #334155; margin-bottom: 1rem;'>👆 Sube un archivo para comenzar</h2>
                <p style='color: #64748b; font-size: 1.125rem;'>Procesamiento automático e inteligente</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #94a3b8; padding: 1rem;'><p><strong>Excel Automator Pro</strong> v2.0</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
