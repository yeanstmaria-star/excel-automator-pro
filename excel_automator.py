"""
AUTOMATIZADOR EXCEL PROFESIONAL - VERSIÓN PREMIUM
Diseño limpio, moderno y minimalista

INSTALACIÓN:
pip install streamlit pandas plotly openpyxl xlsxwriter scipy scikit-learn

EJECUTAR:
streamlit run excel_automator.py
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

# =====================================================================
# CONFIGURACIÓN (DEBE IR PRIMERO - ANTES DE CUALQUIER OTRA COSA)
# =====================================================================

st.set_page_config(
    page_title="Excel Automator Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================================
# IMPORTAR SISTEMA DE AUTENTICACIÓN
# ========================================
import auth

# ========================================
# VERIFICAR AUTENTICACIÓN
# ========================================
if not auth.require_auth():
    st.stop()

# ========================================
# VERIFICAR SI DEBE MOSTRAR MI CUENTA
# ========================================
if st.session_state.get('show_account_page', False):
    auth.show_my_account_page()
    st.stop()

# ========================================
# VERIFICAR LÍMITES DE USO
# ========================================
can_use, error_message = auth.check_usage_limit()

if not can_use:
    st.error(f"🔒 {error_message}")
    st.info("💡 **Actualiza a Premium** para análisis ilimitados")
    
    st.markdown("""
    ### ¿Por qué Premium?
    
    ✅ **Análisis ilimitados** - Sin restricciones diarias
    
    ✅ **Archivos más grandes** - Hasta 50 MB
    
    ✅ **Funciones avanzadas** - Todos los tipos de gráficos
    
    ✅ **Exportar PDF** - Guarda tus reportes
    
    ✅ **Sin marca de agua** - Reportes profesionales
    
    [💳 Ver Planes](https://smartappslab.gumroad.com/l/owmzol)
    """)
    
    st.stop()

# =====================================================================
# CSS PREMIUM - DISEÑO VIBRANTE
# =====================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 1rem 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255,255,255,0.2);
        border-radius: 8px;
        padding: 10px 20px;
        color: white;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 100%);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-left: 5px solid #667eea;
        margin: 10px 0;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        transform: translateY(-2px);
    }
    
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
        font-size: 3rem;
    }
    
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 15px;
        border-left: 5px solid #28a745;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .info-card {
        background: rgba(255,255,255,0.95);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ===== BOTÓN SIDEBAR MOBILE - MUY VISIBLE ===== */
    button[kind="header"] {
        background-color: #ffa500 !important;
        color: white !important;
        border: 3px solid white !important;
        border-radius: 8px !important;
        padding: 8px !important;
        box-shadow: 0 4px 12px rgba(255, 165, 0, 0.6) !important;
    }
    
    button[kind="header"]:hover {
        background-color: #ff8c00 !important;
        transform: scale(1.1) !important;
    }
    
    /* Icono del sidebar más visible */
    button[kind="header"] svg {
        stroke: white !important;
        stroke-width: 3 !important;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)) !important;
    }
    
    /* Asegurar que el botón sea grande en mobile */
    @media (max-width: 768px) {
        button[kind="header"] {
            width: 50px !important;
            height: 50px !important;
            position: fixed !important;
            top: 10px !important;
            left: 10px !important;
            z-index: 999999 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# FUNCIONES AUXILIARES
# =====================================================================

def detect_outliers(df, column):
    """Detecta outliers usando IQR"""
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
    """Genera insights automáticos"""
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
    """Crea Excel formateado"""
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
# INTERFAZ PRINCIPAL
# =====================================================================

def main():
    
    # HEADER
    st.markdown("""
        <div style='text-align: center; margin-bottom: 3rem;'>
            <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>📊 Excel Automator Pro</h1>
            <p style='color: #64748b; font-size: 1.125rem;'>
                Analiza y procesa tus datos en segundos
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("### ⚡ Procesamiento Automático")
        
        st.markdown("""
        **🤖 Al cargar tu archivo:**
        ✅ Limpieza automática de datos
        ✅ Ordenamiento cronológico
        ✅ Eliminación de duplicados
        ✅ Detección de outliers
        
        **📊 Análisis Inteligente:**
        ✅ Estadísticas descriptivas
        ✅ Correlaciones automáticas
        ✅ Insights generados por IA
        
        **📈 Visualizaciones:**
        ✅ Múltiples gráficos profesionales
        ✅ Interactivos y exportables
        
        **📥 Exportación Premium:**
        ✅ Excel formateado
        ✅ CSV optimizado
        ✅ Reportes con estadísticas
        """)
        
        st.markdown("---")
        st.success("💡 Todo el procesamiento es automático e inteligente")
    
    # UPLOAD
    uploaded_file = st.file_uploader(
        "Arrastra tu archivo Excel o CSV aquí",
        type=['xlsx', 'xls', 'csv'],
        help="Formatos soportados: .xlsx, .xls, .csv"
    )
    
    if uploaded_file is not None:
        try:
            # Leer archivo
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8')
                except:
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8', quotechar='"', skipinitialspace=True)
                    except:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, encoding='utf-8')
                df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
            else:
                df = pd.read_excel(uploaded_file)
            
            # PROCESAMIENTO AUTOMÁTICO
            st.info("🔧 Procesando y optimizando datos automáticamente...")
            
            df_original = df.copy()
            initial_stats = {
                'rows': len(df),
                'cols': len(df.columns),
                'nulls': df.isnull().sum().sum(),
                'duplicates': df.duplicated().sum()
            }
            
            # Limpiar
            df = df.dropna(axis=1, how='all')
            df = df.dropna(how='all')
            
            # Ordenar por fecha
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
                st.success(f"✅ Datos ordenados cronológicamente por '{date_cols[0]}'")
            
            # Limpiar espacios
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
            
            # Eliminar duplicados
            duplicates_removed = df.duplicated().sum()
            if duplicates_removed > 0:
                df = df.drop_duplicates().reset_index(drop=True)
            
            final_stats = {
                'rows': len(df),
                'cols': len(df.columns),
                'nulls': df.isnull().sum().sum(),
                'duplicates': df.duplicated().sum()
            }
            
            # Mostrar resumen
            if initial_stats != final_stats:
                st.markdown("""
                    <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                                padding: 20px; border-radius: 12px; margin: 20px 0;'>
                        <h3 style='color: white; margin: 0 0 15px 0;'>✨ Limpieza Automática Completada</h3>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    rows_cleaned = initial_stats['rows'] - final_stats['rows']
                    st.metric("Filas Eliminadas", rows_cleaned, 
                             delta=f"-{(rows_cleaned/initial_stats['rows']*100):.1f}%" if rows_cleaned > 0 else "0%",
                             delta_color="off")
                with col2:
                    cols_cleaned = initial_stats['cols'] - final_stats['cols']
                    st.metric("Columnas Vacías", cols_cleaned, delta_color="off")
                with col3:
                    st.metric("Duplicados", duplicates_removed, delta_color="off")
                with col4:
                    st.metric("Filas Finales", final_stats['rows'])
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.success(f"✅ Archivo procesado: **{uploaded_file.name}**")

            # INCREMENTAR USO
            if st.session_state.user_tier == 'free':
                auth.increment_usage()
                st.success(f"✅ Análisis completado! ({st.session_state.daily_uses}/3 usados hoy)")
            
            # TABS
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Resumen", 
                "🔍 Explorar", 
                "📈 Gráficos",
                "💾 Exportar"
            ])
            
            # TAB 1: RESUMEN
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
                    duplicates = df.duplicated().sum()
                    st.metric("Duplicados", duplicates)
                
                st.markdown("---")
                
                st.markdown("### 🧠 Insights Automáticos")
                insights = generate_insights(df)
                for insight in insights:
                    st.info(insight)
                
                st.markdown("---")
                
                st.markdown("### Vista Previa")
                
                search = st.text_input("🔍 Buscar en los datos", placeholder="Escribe para buscar...")
                
                if search:
                    mask = df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
                    filtered = df[mask]
                    st.caption(f"Mostrando {len(filtered)} resultados")
                    st.dataframe(filtered.head(50), use_container_width=True)
                else:
                    st.dataframe(df.head(100), use_container_width=True)
            
            # TAB 2: EXPLORAR
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
                        selected = st.selectbox("Selecciona columna", numeric_cols, key="explore_numeric_col")
                        
                        col_data = df[selected].dropna()
                        
                        st.metric("Promedio", f"{col_data.mean():.2f}")
                        st.metric("Mediana", f"{col_data.median():.2f}")
                        st.metric("Desv. Estándar", f"{col_data.std():.2f}")
                        
                        outliers, _, _ = detect_outliers(df, selected)
                        if outliers is not None and len(outliers) > 0:
                            st.warning(f"⚠️ {len(outliers)} outliers detectados")
                    else:
                        st.info("No hay columnas numéricas")
                
                st.markdown("---")
                
                st.markdown("#### Top Valores")
                text_cols = df.select_dtypes(include=['object']).columns.tolist()
                if text_cols:
                    col_selected = st.selectbox("Columna", text_cols, key="explore_text_col")
                    top_n = st.slider("Mostrar top", 5, 20, 10, key="explore_top_slider")
                    
                    value_counts = df[col_selected].value_counts().head(top_n)
                    
                    fig = px.bar(
                        x=value_counts.values,
                        y=value_counts.index,
                        orientation='h',
                        labels={'x': 'Frecuencia', 'y': col_selected},
                        color=value_counts.values,
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(height=500, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            
            # TAB 3: GRÁFICOS
            with tab3:
                st.markdown("### Visualizaciones")
                
                viz_type = st.selectbox(
                    "Tipo de gráfico",
                    ["Histograma", "Box Plot", "Scatter Plot", "Correlación", "Pie Chart"]
                )
                
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if viz_type == "Histograma" and numeric_cols:
                    col = st.selectbox("Columna", numeric_cols, key="hist_col")
                    bins = st.slider("Bins", 10, 100, 30, key="hist_bins")
                    
                    fig = px.histogram(df, x=col, nbins=bins, color_discrete_sequence=['#8b5cf6'])
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Box Plot" and numeric_cols:
                    col = st.selectbox("Columna", numeric_cols, key="box_col")
                    fig = px.box(df, y=col, color_discrete_sequence=['#10b981'])
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Scatter Plot" and len(numeric_cols) >= 2:
                    col1, col2 = st.columns(2)
                    with col1:
                        x = st.selectbox("Eje X", numeric_cols, key="scatter_x")
                    with col2:
                        y = st.selectbox("Eje Y", numeric_cols, index=1 if len(numeric_cols) > 1 else 0, key="scatter_y")
                    
                    fig = px.scatter(df, x=x, y=y, trendline="ols", color_discrete_sequence=['#f59e0b'])
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Correlación" and len(numeric_cols) >= 2:
                    corr = df[numeric_cols].corr()
                    fig = px.imshow(corr, text_auto='.2f', aspect="auto", color_continuous_scale='RdBu_r')
                    st.plotly_chart(fig, use_container_width=True)
                
                elif viz_type == "Pie Chart":
                    text_cols = df.select_dtypes(include=['object']).columns.tolist()
                    if text_cols:
                        col = st.selectbox("Columna", text_cols, key="pie_col")
                        top = st.slider("Top N", 3, 15, 8, key="pie_top")
                        
                        values = df[col].value_counts().head(top)
                        fig = px.pie(values=values.values, names=values.index, hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)
            
            # TAB 4: EXPORTAR
            with tab4:
                st.markdown("### Exportar Datos Procesados")
                
                st.info("💡 Los datos ya fueron limpiados y ordenados automáticamente")
                
                st.markdown("#### Opciones Adicionales")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    remove_nulls = st.checkbox("Eliminar filas con valores nulos", value=False)
                    include_stats = st.checkbox("Incluir hoja de estadísticas", value=True)
                
                with col2:
                    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                    if numeric_cols:
                        remove_outliers = st.checkbox("Eliminar outliers extremos", value=False)
                
                if st.button("🎯 Preparar Descarga", type="primary"):
                    df_export = df.copy()
                    
                    if remove_nulls:
                        df_export = df_export.dropna()
                    
                    st.success("✅ Datos listos para exportar")
                    st.session_state['export_df'] = df_export
                
                st.markdown("---")
                
                if 'export_df' in st.session_state:
                    df_to_export = st.session_state['export_df']
                    
                    st.markdown("#### 📥 Descargar Archivo Procesado")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        csv_data = df_to_export.to_csv(index=False).encode('utf-8-sig')
                        st.download_button(
                            "📥 Descargar CSV",
                            data=csv_data,
                            file_name=f"datos_limpios_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        excel_data = create_excel_download(df_to_export, include_stats)
                        st.download_button(
                            "📥 Descargar Excel",
                            data=excel_data,
                            file_name=f"datos_limpios_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    st.markdown("#### 👀 Vista Previa")
                    st.dataframe(df_to_export.head(20), use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Verifica que el archivo esté en formato correcto")
    
    else:
        # Landing
        st.markdown("""
            <div style='text-align: center; padding: 60px 20px; 
                        background: white; border-radius: 16px; 
                        box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <h2 style='color: #334155; margin-bottom: 1rem;'>
                    👆 Sube un archivo para comenzar
                </h2>
                <p style='color: #64748b; font-size: 1.125rem;'>
                    Procesamiento automático e inteligente de datos
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #94a3b8; padding: 1rem;'>
            <p><strong>Excel Automator Pro</strong> v2.0 | Hecho con Streamlit</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

