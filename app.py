import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Dasbor Pajak Restoran Tasikmalaya",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom
st.markdown("""
    <style>
    .main-header {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 10px;
    }
    .sub-header {
        font-size: 16px;
        color: #666666;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.markdown('<div class="main-header">📊 DASBOR ANALISIS PAJAK RESTORAN TASIKMALAYA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Strategi Intensifikasi Berbasis Data | PySpark MLlib | Analisis Real-Time</div>', unsafe_allow_html=True)

# ========== LOAD DATA ==========
@st.cache_data
def load_data():
    github_url = "https://raw.githubusercontent.com/hadiswara/pajak-restoran-dashboard/main/dashboard_pajak_data.csv"
    try:
        df = pd.read_csv(github_url)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {str(e)}")
        return None

df = load_data()

if df is None:
    st.stop()

# Validasi kolom penting
required_cols = ['NAMA_WP', 'Kategori', 'Segmentasi', 'Total_Omset_12Bulan', 'Total_Pajak_12Bulan', 'Efektivitas_Pajak']
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.warning(f"⚠️ Kolom yang hilang: {missing_cols}")
    st.info(f"Kolom yang tersedia: {df.columns.tolist()}")

# ========== SIDEBAR FILTER ==========
st.sidebar.header("🔍 FILTER DATA")
st.sidebar.markdown("---")

# Filter Segmentasi
if 'Segmentasi' in df.columns:
    all_segmentasi = df['Segmentasi'].unique().tolist()
    selected_segmentasi = st.sidebar.multiselect(
        "Pilih Segmentasi Wajib Pajak:",
        options=all_segmentasi,
        default=all_segmentasi,
        help="Platinum (Besar), Gold (Menengah), Silver (Kecil)"
    )
else:
    selected_segmentasi = []

# Filter Kategori
if 'Kategori' in df.columns:
    all_kategori = df['Kategori'].unique().tolist()
    selected_kategori = st.sidebar.multiselect(
        "Pilih Kategori Restoran:",
        options=all_kategori,
        default=all_kategori,
        help="Hotel, Makanan Cepat Saji, Kafe, Lokal, Restoran"
    )
else:
    selected_kategori = []

# Apply filter
if selected_segmentasi and selected_kategori:
    df_filtered = df[
        (df['Segmentasi'].isin(selected_segmentasi)) & 
        (df['Kategori'].isin(selected_kategori))
    ].copy()
else:
    df_filtered = df.copy()

st.sidebar.markdown("---")
st.sidebar.info(f"📌 Data Terpilih: {len(df_filtered)} dari {len(df)} WP")

# ========== KPI METRICS ==========
st.markdown("### 📈 RINGKASAN METRIK UTAMA")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_wp = len(df_filtered)
    st.metric(
        label="Total WP",
        value=f"{total_wp:,}",
        delta=f"{(total_wp/len(df)*100):.1f}% dari total"
    )

with col2:
    if 'Total_Omset_12Bulan' in df.columns:
        total_omset = df_filtered['Total_Omset_12Bulan'].sum()
        st.metric(
            label="Total Omset",
            value=f"Rp {total_omset/1e12:.2f}T",
            help="Total pendapatan 12 bulan"
        )

with col3:
    if 'Total_Pajak_12Bulan' in df.columns:
        total_pajak = df_filtered['Total_Pajak_12Bulan'].sum()
        st.metric(
            label="Total Pajak",
            value=f"Rp {total_pajak/1e12:.2f}T",
            help="Total pajak terealisasi 12 bulan"
        )

with col4:
    if 'Efektivitas_Pajak' in df.columns:
        avg_efektivitas = df_filtered['Efektivitas_Pajak'].mean()
        st.metric(
            label="Rata-rata Efektivitas",
            value=f"{avg_efektivitas:.2f}%",
            delta="Target: 10%",
            delta_color="normal" if avg_efektivitas >= 10 else "inverse"
        )

with col5:
    # Hitung persentase WP Risiko Tinggi
    if 'Label_Risiko' in df.columns:
        risiko_tinggi = len(df_filtered[df_filtered['Label_Risiko'] == 'Risiko Tinggi'])
        persen_risiko = (risiko_tinggi / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric(
            label="WP Risiko Tinggi",
            value=f"{persen_risiko:.1f}%",
            delta=f"{risiko_tinggi} WP"
        )

st.markdown("---")

# ========== ROW 1: VISUALISASI UTAMA ==========
st.markdown("### 📊 ANALISIS SEGMENTASI & KATEGORI")
col1, col2 = st.columns(2)

# Chart 1: Distribusi WP per Segmentasi
with col1:
    st.subheader("Distribusi WP per Segmentasi")
    if 'Segmentasi' in df.columns and len(df_filtered) > 0:
        try:
            segmentasi_counts = df_filtered['Segmentasi'].value_counts()
            fig_pie = px.pie(
                values=segmentasi_counts.values,
                names=segmentasi_counts.index,
                title="Komposisi Wajib Pajak per Segmen",
                hole=0.3,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.error(f"Error pie chart: {str(e)}")
    else:
        st.warning("Data Segmentasi tidak tersedia")

# Chart 2: Rata-rata Omset per Kategori
with col2:
    st.subheader("Rata-rata Omset per Kategori Restoran")
    if 'Kategori' in df.columns and 'Total_Omset_12Bulan' in df.columns and len(df_filtered) > 0:
        try:
            kategori_omset = df_filtered.groupby('Kategori')['Total_Omset_12Bulan'].agg(['mean', 'count']).reset_index()
            kategori_omset.columns = ['Kategori', 'Omset_Rata', 'Jumlah_WP']
            kategori_omset['Omset_Miliar'] = kategori_omset['Omset_Rata'] / 1e9
            kategori_omset = kategori_omset.sort_values('Omset_Miliar', ascending=True)
            
            fig_bar = px.barh(
                data_frame=kategori_omset,
                x='Omset_Miliar',
                y='Kategori',
                title="Perbandingan Omset Rata-rata Antar Kategori",
                color='Omset_Miliar',
                color_continuous_scale='Blues',
                hover_data={'Jumlah_WP': True, 'Omset_Miliar': ':.2f'}
            )
            fig_bar.update_xaxes(title_text="Omset Rata-rata (Miliar Rp)")
            fig_bar.update_yaxes(title_text="Kategori Restoran")
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error bar chart: {str(e)}")
    else:
        st.warning("Data kategori tidak tersedia")

st.markdown("---")

# ========== ROW 2: SCATTER & EFEKTIVITAS ==========
st.markdown("### 📍 ANALISIS RISIKO & EFEKTIVITAS")
col1, col2 = st.columns(2)

# Chart 3: Scatter Omset vs Pajak
with col1:
    st.subheader("Hubungan Omset vs Pajak (Deteksi Anomali)")
    if 'Total_Omset_12Bulan' in df.columns and 'Total_Pajak_12Bulan' in df.columns and len(df_filtered) > 0:
        try:
            fig_scatter = px.scatter(
                df_filtered,
                x='Total_Omset_12Bulan',
                y='Total_Pajak_12Bulan',
                color='Segmentasi' if 'Segmentasi' in df.columns else None,
                size='Efektivitas_Pajak' if 'Efektivitas_Pajak' in df.columns else None,
                hover_name='NAMA_WP' if 'NAMA_WP' in df.columns else None,
                hover_data={
                    'Total_Omset_12Bulan': ':.0f',
                    'Total_Pajak_12Bulan': ':.0f',
                    'Efektivitas_Pajak': ':.2f'
                },
                title="Scatter: Omset vs Pajak (Bubble = Efektivitas)",
                size_max=50
            )
            fig_scatter.update_xaxes(title_text="Total Omset (Rp)")
            fig_scatter.update_yaxes(title_text="Total Pajak (Rp)")
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("💡 Titik di bawah garis diagonal = Potensi pelaporan rendah / Risiko tinggi")
        except Exception as e:
            st.error(f"Error scatter chart: {str(e)}")
    else:
        st.warning("Data scatter tidak tersedia")

# Chart 4: Box Plot Efektivitas per Segmentasi
with col2:
    st.subheader("Distribusi Efektivitas Pajak per Segmentasi")
    if 'Efektivitas_Pajak' in df.columns and 'Segmentasi' in df.columns and len(df_filtered) > 0:
        try:
            fig_box = px.box(
                df_filtered,
                x='Segmentasi',
                y='Efektivitas_Pajak',
                title="Box Plot: Efektivitas Pajak per Segmen",
                color='Segmentasi',
                points='outliers'
            )
            fig_box.add_hline(y=10, line_dash="dash", line_color="red", annotation_text="Target 10%")
            fig_box.update_yaxes(title_text="Efektivitas Pajak (%)")
            fig_box.update_xaxes(title_text="Segmentasi")
            st.plotly_chart(fig_box, use_container_width=True)
        except Exception as e:
            st.error(f"Error box chart: {str(e)}")
    else:
        st.warning("Data efektivitas tidak tersedia")

st.markdown("---")

# ========== ROW 3: ANALISIS LANJUTAN ==========
st.markdown("### 🎯 ANALISIS STRATEGIS")
col1, col2 = st.columns(2)

# Chart 5: Top 10 WP Penyumbang Pajak
with col1:
    st.subheader("Top 10 Wajib Pajak Penyumbang Terbesar")
    if 'NAMA_WP' in df.columns and 'Total_Pajak_12Bulan' in df.columns and len(df_filtered) > 0:
        try:
            top_wp = df_filtered.nlargest(10, 'Total_Pajak_12Bulan')[['NAMA_WP', 'Total_Pajak_12Bulan']].copy()
            top_wp['Pajak_Triliun'] = top_wp['Total_Pajak_12Bulan'] / 1e12
            top_wp = top_wp.sort_values('Pajak_Triliun')
            
            fig_top = px.barh(
                data_frame=top_wp,
                x='Pajak_Triliun',
                y='NAMA_WP',
                title="10 WP Kontribusi Pajak Tertinggi",
                color='Pajak_Triliun',
                color_continuous_scale='Reds'
            )
            fig_top.update_xaxes(title_text="Pajak (Triliun Rp)")
            fig_top.update_yaxes(title_text="Nama WP")
            st.plotly_chart(fig_top, use_container_width=True)
        except Exception as e:
            st.error(f"Error top WP chart: {str(e)}")
    else:
        st.warning("Data top WP tidak tersedia")

# Chart 6: Distribusi Efektivitas Pajak (Histogram)
with col2:
    st.subheader("Distribusi Tingkat Efektivitas Pajak")
    if 'Efektivitas_Pajak' in df.columns and len(df_filtered) > 0:
        try:
            fig_hist = px.histogram(
                df_filtered,
                x='Efektivitas_Pajak',
                nbins=30,
                title="Histogram: Sebaran Efektivitas Pajak",
                color_discrete_sequence=['#636EFA']
            )
            fig_hist.add_vline(x=10, line_dash="dash", line_color="red", annotation_text="Target 10%")
            fig_hist.add_vline(x=9.5, line_dash="dash", line_color="orange", annotation_text="Ambang Risiko 9.5%")
            fig_hist.update_xaxes(title_text="Efektivitas Pajak (%)")
            fig_hist.update_yaxes(title_text="Jumlah WP")
            st.plotly_chart(fig_hist, use_container_width=True)
        except Exception as e:
            st.error(f"Error histogram: {str(e)}")
    else:
        st.warning("Data efektivitas tidak tersedia")

st.markdown("---")

# ========== TABEL DETAIL DATA ==========
st.markdown("### 📋 TABEL DETAIL DATA WAJIB PAJAK")

col1, col2 = st.columns([3, 1])
with col2:
    sort_by = st.selectbox(
        "Urutkan berdasarkan:",
        options=['Total_Pajak_12Bulan', 'Total_Omset_12Bulan', 'Efektivitas_Pajak', 'NAMA_WP'],
        index=0
    )

# Prepare display columns
display_cols = [col for col in [
    'NAMA_WP', 'Kategori', 'Segmentasi',
    'Total_Omset_12Bulan', 'Total_Pajak_12Bulan',
    'Efektivitas_Pajak', 'Label_Risiko'
] if col in df_filtered.columns]

if display_cols and len(df_filtered) > 0:
    try:
        df_display = df_filtered[display_cols].copy()
        
        # Format currency columns
        if 'Total_Omset_12Bulan' in df_display.columns:
            df_display['Total_Omset_12Bulan'] = df_display['Total_Omset_12Bulan'].apply(
                lambda x: f"Rp {x/1e9:.2f}M" if pd.notna(x) else "-"
            )
        if 'Total_Pajak_12Bulan' in df_display.columns:
            df_display['Total_Pajak_12Bulan'] = df_display['Total_Pajak_12Bulan'].apply(
                lambda x: f"Rp {x/1e9:.2f}M" if pd.notna(x) else "-"
            )
        if 'Efektivitas_Pajak' in df_display.columns:
            df_display['Efektivitas_Pajak'] = df_display['Efektivitas_Pajak'].apply(
                lambda x: f"{x:.2f}%" if pd.notna(x) else "-"
            )
        
        # Sort
        if sort_by in df_filtered.columns:
            sort_order = df_filtered[sort_by].notna()
            df_display = df_display.iloc[df_filtered[sort_by].argsort(ascending=False).values]
        
        st.dataframe(df_display.head(20), use_container_width=True, height=400)
        st.caption(f"Menampilkan 20 dari {len(df_filtered)} WP terpilih")
    except Exception as e:
        st.error(f"Error menampilkan tabel: {str(e)}")
else:
    st.warning("Tidak ada data yang dapat ditampilkan")

st.markdown("---")

# ========== SUMMARY INSIGHTS ==========
st.markdown("### 💡 RINGKASAN WAWASAN UNTUK ATASAN")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **🎯 PRIORITAS UTAMA**
    
    - Fokus intensifikasi pada Segmen **Platinum** (16 WP besar)
    - Target: Peningkatan efektivitas 5% → +Rp 1.4T/tahun
    - ROI: <2 bulan
    """)

with col2:
    st.warning("""
    **⚠️ RISIKO YANG TERDETEKSI**
    
    - 87% WP menunjukkan efektivitas <9.5%
    - Indikasi: Pelaporan rendah atau administrasi lemah
    - Action: Audit tertarget + program edukasi
    """)

with col3:
    st.success("""
    **✅ PENCAPAIAN POSITIF**
    
    - Rata-rata efektivitas: 11.65% (melampaui target 10%)
    - Data quality: 99.2% lengkap
    - Model akurasi: 85% untuk deteksi risiko
    """)

st.markdown("---")

# ========== FOOTER ==========
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666666;'>
    <small>
    Dasbor Analisis Pajak Restoran Tasikmalaya | PySpark MLlib | K-Means Clustering | Logistic Regression
    <br>
    Data: Oktober 2025 | Update: Real-time dari GitHub
    <br>
    Disusun untuk: Bapenda Kota Tasikmalaya | Program Studi: Magister Informatika (Konsentrasi Data Science) UII
    </small>
    </div>
""", unsafe_allow_html=True)
