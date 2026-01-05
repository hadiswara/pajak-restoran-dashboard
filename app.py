import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Pajak Restoran Tasikmalaya", layout="wide")

st.title("Dashboard Analisis Pajak Restoran Tasikmalaya")
st.markdown("Data: Oktober 2025 | Analisis dengan PySpark MLlib")

# Load Data dari GitHub Raw URL
github_url = "https://raw.githubusercontent.com/hadiswara/pajak-restoran-dashboard/main/dashboard_pajak_data.csv"

try:
    df = pd.read_csv(github_url)
    st.success("Data berhasil dimuat dari GitHub")
except:
    st.error("Gagal load data. Pastikan URL GitHub benar dan file ada.")
    st.stop()

# SIDEBAR FILTER
st.sidebar.header("Filter Data")
segmentasi_filter = st.sidebar.multiselect(
    "Pilih Segmentasi:",
    options=df['Segmentasi'].unique(),
    default=df['Segmentasi'].unique()
)

kategori_filter = st.sidebar.multiselect(
    "Pilih Kategori Restoran:",
    options=df['Kategori'].unique(),
    default=df['Kategori'].unique()
)

# Apply Filter
df_filtered = df[
    (df['Segmentasi'].isin(segmentasi_filter)) & 
    (df['Kategori'].isin(kategori_filter))
]

# METRICS ROW
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total WP", len(df_filtered))

with col2:
    total_omset = df_filtered['Total_Omset_12Bulan'].sum() / 1e12
    st.metric("Total Omset (Triliun)", f"Rp {total_omset:.2f}T")

with col3:
    total_pajak = df_filtered['Total_Pajak_12Bulan'].sum() / 1e12
    st.metric("Total Pajak (Triliun)", f"Rp {total_pajak:.2f}T")

with col4:
    avg_efektivitas = df_filtered['Efektivitas_Pajak'].mean()
    st.metric("Rata-rata Efektivitas", f"{avg_efektivitas:.2f}%")

# CHARTS
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Segmentasi")
    segmentasi_counts = df_filtered['Segmentasi'].value_counts()
    fig_pie = px.pie(
        values=segmentasi_counts.values,
        names=segmentasi_counts.index,
        title="WP per Segmentasi"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Rata-rata Omset per Kategori")
    kategori_omset = df_filtered.groupby('Kategori')['Total_Omset_12Bulan'].mean().sort_values(ascending=True) / 1e9
    
    fig_bar = px.barh(
        x=kategori_omset.values,
        y=kategori_omset.index,
        title="Rata-rata Omset per Kategori (Miliar Rp)",
        labels={'x': 'Omset (Miliar Rp)', 'y': 'Kategori'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# SCATTER PLOT
st.subheader("Hubungan Omset vs Pajak")
fig_scatter = px.scatter(
    df_filtered,
    x='Total_Omset_12Bulan',
    y='Total_Pajak_12Bulan',
    color='Segmentasi',
    size='Efektivitas_Pajak',
    hover_name='NAMA_WP',
    title="Scatter: Omset vs Pajak (Size = Efektivitas)",
    labels={
        'Total_Omset_12Bulan': 'Omset (Rp)',
        'Total_Pajak_12Bulan': 'Pajak (Rp)'
    }
)
st.plotly_chart(fig_scatter, use_container_width=True)

# TABLE DATA
st.markdown("---")
st.subheader("Data Detail")
display_cols = ['NAMA_WP', 'Kategori', 'Total_Omset_12Bulan', 'Total_Pajak_12Bulan', 'Efektivitas_Pajak', 'Segmentasi']
st.dataframe(df_filtered[display_cols].sort_values('Total_Omset_12Bulan', ascending=False), use_container_width=True)

# FOOTER
st.markdown("---")

st.markdown("*Dashboard dibuat dengan Streamlit | Data dari analisis PySpark MLlib*")

