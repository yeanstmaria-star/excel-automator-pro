"""
AUTOMATIZADOR EXCEL PROFESIONAL - TEST SIN AUTH
"""

import streamlit as st
import pandas as pd
import plotly.express as px
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
    initial_sidebar_state="expanded"
)

# CSS MÍNIMO
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #2d3748;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stHeader"],
    #MainMenu,
    footer {
        display: none;
    }
</style>
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
    st.title("📊 Excel Automator Pro")
    st.caption("Analiza y procesa tus datos en segundos")
    
    # SIDEBAR
    with st.sidebar:
        st.markdown("### ⚡ Procesamiento Automático")
        st.markdown("""
        **🤖 Al cargar tu archivo:**
        ✅ Limpieza automática
        ✅ Ordenamiento cronológico
        ✅ Eliminación de duplicados
        
        **📊 Análisis:**
        ✅ Estadísticas descriptivas
        ✅ Correlaciones automáticas
        
        **📈 Visualizaciones:**
        ✅ Gráficos profesionales
        """)
        st.success("💡 Todo automático")
    
    uploaded_file = st.file_uploader("Arrastra tu archivo Excel o CSV aquí", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file:
        try:
            # Leer archivo
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
            
            # Limpiar
            initial_rows = len(df)
            df = df.dropna(axis=1, how='all').dropna(how='all')
            
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
                df = df.sort_values(by=date_cols[0]).reset_index(drop=True)
                st.success(f"✅ Ordenado por '{date_cols[0]}'")
            
            # Duplicados
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                df = df.drop_duplicates().reset_index(drop=True)
                st.success(f"✅ {duplicates} duplicados eliminados")
            
            st.success(f"✅ Archivo procesado: **{uploaded_file.name}**")
            
            # TABS
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen", "🔍 Explorar", "📈 Gráficos", "💾 Exportar"])
            
            with tab1:
                st.markdown("### Resumen General")
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
                st.markdown("### Información de Columnas")
                info_list = []
                for col in df.columns:
                    info_list.append({
                        'Columna': col,
                        'Tipo': str(df[col].dtype),
                        'Únicos': df[col].nunique(),
                        'Nulos': df[col].isnull().sum()
                    })
                st.dataframe(pd.DataFrame(info_list), use_container_width=True, hide_index=True)
            
            with tab3:
                st.markdown("### Visualizaciones")
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if numeric_cols:
                    viz_type = st.selectbox("Tipo de gráfico", ["Histograma", "Box Plot", "Correlación"])
                    
                    if viz_type == "Histograma":
                        col = st.selectbox("Columna", numeric_cols)
                        fig = px.histogram(df, x=col, color_discrete_sequence=['#8b5cf6'])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Box Plot":
                        col = st.selectbox("Columna", numeric_cols)
                        fig = px.box
                        col = st.selectbox("Columna", numeric_cols)
                        fig = px.box(df, y=col, color_discrete_sequence=['#10b981'])
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif viz_type == "Correlación" and len(numeric_cols) >= 2:
                        corr = df[numeric_cols].corr()
                        fig = px.imshow(corr, text_auto='.2f', aspect="auto", color_continuous_scale='RdBu_r')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No hay columnas numéricas para visualizar")
            
            with tab4:
                st.markdown("### Exportar Datos Procesados")
                st.info("💡 Los datos ya fueron limpiados automáticamente")
                
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
        st.markdown("""
            <div style='text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
                <h2 style='color: #334155; margin-bottom: 1rem;'>👆 Sube un archivo para comenzar</h2>
                <p style='color: #64748b; font-size: 1.125rem;'>Procesamiento automático e inteligente de datos</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<div style='text-align: center; color: #94a3b8;'><p><strong>Excel Automator Pro</strong> v2.0</p></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
