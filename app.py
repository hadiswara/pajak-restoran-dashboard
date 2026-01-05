import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dasbor Pajak Restoran Tasikmalaya", layout="wide")

st.title("Dasbor Analisis Pajak Restoran Tasikmalaya")
st.markdown("Data: Oktober 2025 | Analisis dengan PySpark MLlib")

# Load Data
github_url = "https://raw.githubusercontent.com/hadiswara/pajak-restoran-dashboard/main/dashboard_pajak_data.csv"

try:
    df = pd.read_csv(github_url)
    st.success("Data berhasil dimuat dari GitHub")
except Exception as e:
    st.error(f"Gagal load data: {str(e)}")
    st.stop()

# Debug: Tampilkan nama kolom
st.sidebar.write("Kolom yang tersedia:", df.columns.tolist())

# FILTER
st.sidebar.header("Filter Data")
if 'Segmentasi' in df.columns:
    segmentasi_filter = st.sidebar.multiselect(
        "Pilih Segmentasi:",
        options=df['Segmentasi'].unique(),
        default=df['Segmentasi'].unique()
    )
else:
    segmentasi_filter = df['Segmentasi'].unique() if 'Segmentasi' in df.columns else []

if 'Kategori' in df.columns:
    kategori_filter = st.sidebar.multiselect(
        "Pilih Kategori Restoran:",
        options=df['Kategori'].unique(),
        default=df['Kategori'].unique()
    )
else:
    kategori_filter = df['Kategori'].unique() if 'Kategori' in df.columns else []

# APPLY FILTER
df_filtered = df[
    (df['Segmentasi'].isin(segmentasi_filter)) & 
    (df['Kategori'].isin(kategori_filter))
]

# METRICS
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total WP", len(df_filtered))

with col2:
    if 'Total_Omset_12Bulan' in df.columns:
        total_omset = df_filtered['Total_Omset_12Bulan'].sum() / 1e12
        st.metric("Total Omset (Triliun)", f"Rp {total_omset:.2f}T")

with col3:
    if 'Total_Pajak_12Bulan' in df.columns:
        total_pajak = df_filtered['Total_Pajak_12Bulan'].sum() / 1e12
        st.metric("Total Pajak (Triliun)", f"Rp {total_pajak:.2f}T")

with col4:
    if 'Efektivitas_Pajak' in df.columns:
        avg_efektivitas = df_filtered['Efektivitas_Pajak'].mean()
        st.metric("Rata-rata Efektivitas", f"{avg_efektivitas:.2f}%")

st.markdown("---")

# CHARTS
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Segmentasi")
    if 'Segmentasi' in df.columns:
        segmentasi_counts = df_filtered['Segmentasi'].value_counts()
        fig_pie = px.pie(
with col2:
    st.subheader("Rata-rata Omset per Kategori")
    if 'Kategori' in df.columns and 'Total_Omset_12Bulan' in df.columns:
        try:
            kategori_data = df_filtered.groupby('Kategori')['Total_Omset_12Bulan'].mean().reset_index()
            kategori_data.columns = ['Kategori', 'Omset_Rata']
            kategori_data['Omset_Miliar'] = kategori_data['Omset_Rata'] / 1e9
            kategori_data = kategori_data.sort_values('Omset_Miliar', ascending=True)
            
            fig_bar = px.barh(
                data_frame=kategori_data,
                x='Omset_Miliar',
                y='Kategori',
                title="Rata-rata Omset per Kategori"
            )
            fig_bar.update_xaxes(title_text="Omset (Miliar Rp)")
            fig_bar.update_yaxes(title_text="Kategori")
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error di chart: {str(e)}")
    else:
        st.warning("Kolom Kategori atau Total_Omset_12Bulan tidak ditemukan")

            xaxis_title="Omset (Miliar Rp)",
            yaxis_title="Kategori"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# SCATTER
st.subheader("Hubungan Omset vs Pajak")
if 'Total_Omset_12Bulan' in df.columns and 'Total_Pajak_12Bulan' in df.columns:
    fig_scatter = px.scatter(
        df_filtered,
        x='Total_Omset_12Bulan',
        y='Total_Pajak_12Bulan',
        color='Segmentasi' if 'Segmentasi' in df.columns else None,
        size='Efektivitas_Pajak' if 'Efektivitas_Pajak' in df.columns else None,
        hover_name='NAMA_WP' if 'NAMA_WP' in df.columns else None,
        title="Scatter: Omset vs Pajak"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# TABLE
st.markdown("---")
st.subheader("Data Detail")
display_cols = [col for col in ['NAMA_WP', 'Kategori', 'Total_Omset_12Bulan', 'Total_Pajak_12Bulan', 'Efektivitas_Pajak', 'Segmentasi'] if col in df.columns]
if display_cols and 'Total_Omset_12Bulan' in df.columns:
    st.dataframe(df_filtered[display_cols].sort_values('Total_Omset_12Bulan', ascending=False), use_container_width=True)

st.markdown("---")
st.markdown("*Dasbor dibuat dengan Streamlit | Data dari analisis PySpark MLlib*")

