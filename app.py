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

# CSS Custom dengan tema profesional
st.markdown("""
    <style>
    .main-header {
        font-size: 32px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 5px;
        text-align: center;
    }
    .sub-header {
        font-size: 16px;
        color: #666666;
        margin-bottom: 30px;
        text-align: center;
    }
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .section-header {
        font-size: 18px;
        font-weight: bold;
        color: #1f77b4;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ========== HEADER ==========
st.markdown('<div class="main-header">📊 DASBOR ANALISIS PAJAK RESTORAN TASIKMALAYA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Strategi Intensifikasi Berbasis Data | PySpark MLlib | Analisis Komprehensif</div>', unsafe_allow_html=True)

# ========== LOAD DATA ==========
@st.cache_data
def load_data():
    github_url = "https://raw.githubusercontent.com/hadiswara/pajak-restoran-dashboard/main/dashboard_pajak_data.csv"
    try:
        df = pd.read_csv(github_url)
        # Konversi kolom numerik
        numeric_cols = ['Total_Omset_12Bulan', 'Total_Pajak_12Bulan', 'Efektivitas_Pajak']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
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
    st.stop()

# ========== SIDEBAR FILTER ==========
st.sidebar.header("🔍 FILTER DATA")
st.sidebar.markdown("---")

# Filter Segmentasi
all_segmentasi = sorted(df['Segmentasi'].dropna().unique().tolist()) if 'Segmentasi' in df.columns else []
selected_segmentasi = st.sidebar.multiselect(
    "Pilih Segmentasi Wajib Pajak:",
    options=all_segmentasi,
    default=all_segmentasi,
    help="Platinum (Besar), Gold (Menengah), Silver (Kecil)"
)

# Filter Kategori
all_kategori = sorted(df['Kategori'].dropna().unique().tolist()) if 'Kategori' in df.columns else []
selected_kategori = st.sidebar.multiselect(
    "Pilih Kategori Restoran:",
    options=all_kategori,
    default=all_kategori,
    help="Hotel, Makanan Cepat Saji, Kafe, Lokal, Restoran"
)

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
st.sidebar.markdown("---")
st.sidebar.caption("Dashboard dibuat dengan Streamlit | Data dari PySpark MLlib")

# ========== KPI METRICS ==========
st.markdown('<div class="section-header">📈 RINGKASAN METRIK UTAMA</div>', unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_wp = len(df_filtered)
    persen = (total_wp / len(df) * 100)
    st.metric(
        label="Total WP",
        value=f"{total_wp:,}",
        delta=f"{persen:.1f}% dari {len(df)}"
    )

with col2:
    total_omset = df_filtered['Total_Omset_12Bulan'].sum()
    st.metric(
        label="Total Omset",
        value=f"Rp {total_omset/1e12:.1f}T",
        help="Total pendapatan 12 bulan (Desember 2024 - November 2025)"
    )

with col3:
    total_pajak = df_filtered['Total_Pajak_12Bulan'].sum()
    st.metric(
        label="Total Pajak",
        value=f"Rp {total_pajak/1e12:.1f}T",
        help="Total pajak terealisasi 12 bulan"
    )

with col4:
    avg_efektivitas = df_filtered['Efektivitas_Pajak'].mean()
    delta_color = "normal" if avg_efektivitas >= 10 else "inverse"
    st.metric(
        label="Rata-rata Efektivitas",
        value=f"{avg_efektivitas:.2f}%",
        delta="Target: 10%",
        delta_color=delta_color
    )

with col5:
    if 'Label_Risiko' in df.columns:
        risiko_tinggi = len(df_filtered[df_filtered['Label_Risiko'] == 'Risiko Tinggi'])
        persen_risiko = (risiko_tinggi / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric(
            label="WP Risiko Tinggi",
            value=f"{persen_risiko:.1f}%",
            delta=f"{risiko_tinggi} WP"
        )
    else:
        st.metric(label="WP Risiko Tinggi", value="N/A")

st.markdown("---")

# ========== ROW 1: VISUALISASI UTAMA ==========
st.markdown('<div class="section-header">📊 ANALISIS SEGMENTASI & KATEGORI</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

# Chart 1: Distribusi WP per Segmentasi
with col1:
    st.subheader("Distribusi WP per Segmentasi")
    if 'Segmentasi' in df_filtered.columns and len(df_filtered) > 0:
        try:
            segmentasi_counts = df_filtered['Segmentasi'].value_counts()
            fig_pie = px.pie(
                values=segmentasi_counts.values,
                names=segmentasi_counts.index,
                title="Komposisi Wajib Pajak per Segmen",
                hole=0.3,
                color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12']
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(size=12))
            fig_pie.update_layout(
                showlegend=True,
                height=450,
                font=dict(size=11),
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        except Exception as e:
            st.error(f"Error pie chart: {str(e)}")
    else:
        st.warning("Data Segmentasi tidak tersedia")

# Chart 2: Rata-rata Omset per Kategori (MENGGUNAKAN bar, bukan barh)
with col2:
    st.subheader("Rata-rata Omset per Kategori Restoran")
    if 'Kategori' in df_filtered.columns and 'Total_Omset_12Bulan' in df_filtered.columns and len(df_filtered) > 0:
        try:
            kategori_omset = df_filtered.groupby('Kategori')['Total_Omset_12Bulan'].agg(['mean', 'count']).reset_index()
            kategori_omset.columns = ['Kategori', 'Omset_Rata', 'Jumlah_WP']
            kategori_omset['Omset_Miliar'] = kategori_omset['Omset_Rata'] / 1e9
            kategori_omset = kategori_omset.sort_values('Omset_Miliar', ascending=False)
            
            # PERBAIKAN: Gunakan bar() bukan barh() untuk vertical bar chart
            fig_bar = px.bar(
                data_frame=kategori_omset,
                x='Kategori',
                y='Omset_Miliar',
                title="Perbandingan Omset Rata-rata Antar Kategori",
                color='Omset_Miliar',
                color_continuous_scale='Blues',
                hover_data={'Jumlah_WP': True, 'Omset_Miliar': ':.2f'}
            )
            fig_bar.update_xaxes(title_text="Kategori Restoran", tickangle=-45)
            fig_bar.update_yaxes(title_text="Omset Rata-rata (Miliar Rp)")
            fig_bar.update_layout(
                height=450,
                font=dict(size=11),
                margin=dict(l=50, r=50, t=40, b=100),
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error bar chart: {str(e)}")
    else:
        st.warning("Data kategori tidak tersedia")

st.markdown("---")

# ========== ROW 2: SCATTER & EFEKTIVITAS ==========
st.markdown('<div class="section-header">📍 ANALISIS RISIKO & EFEKTIVITAS</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

# Chart 3: Scatter Omset vs Pajak
with col1:
    st.subheader("Hubungan Omset vs Pajak (Deteksi Anomali)")
    if 'Total_Omset_12Bulan' in df_filtered.columns and 'Total_Pajak_12Bulan' in df_filtered.columns and len(df_filtered) > 0:
        try:
            fig_scatter = px.scatter(
                df_filtered,
                x='Total_Omset_12Bulan',
                y='Total_Pajak_12Bulan',
                color='Segmentasi' if 'Segmentasi' in df_filtered.columns else None,
                size='Efektivitas_Pajak' if 'Efektivitas_Pajak' in df_filtered.columns else None,
                hover_name='NAMA_WP' if 'NAMA_WP' in df_filtered.columns else None,
                hover_data={
                    'Total_Omset_12Bulan': ':.0f',
                    'Total_Pajak_12Bulan': ':.0f',
                    'Efektivitas_Pajak': ':.2f'
                },
                title="Scatter: Omset vs Pajak (Bubble = Efektivitas)",
                size_max=50,
                color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12']
            )
            fig_scatter.update_xaxes(title_text="Total Omset (Rp)")
            fig_scatter.update_yaxes(title_text="Total Pajak (Rp)")
            fig_scatter.update_layout(
                height=450,
                font=dict(size=10),
                margin=dict(l=50, r=20, t=40, b=50)
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            st.caption("💡 Titik di bawah garis diagonal = Potensi pelaporan rendah (Risiko Tinggi)")
        except Exception as e:
            st.error(f"Error scatter chart: {str(e)}")
    else:
        st.warning("Data scatter tidak tersedia")

# Chart 4: Box Plot Efektivitas per Segmentasi
with col2:
    st.subheader("Distribusi Efektivitas Pajak per Segmentasi")
    if 'Efektivitas_Pajak' in df_filtered.columns and 'Segmentasi' in df_filtered.columns and len(df_filtered) > 0:
        try:
            fig_box = px.box(
                df_filtered,
                x='Segmentasi',
                y='Efektivitas_Pajak',
                title="Box Plot: Efektivitas Pajak per Segmen",
                color='Segmentasi',
                points='outliers',
                color_discrete_sequence=['#3498db', '#e74c3c', '#f39c12']
            )
            fig_box.add_hline(y=10, line_dash="dash", line_color="red", annotation_text="Target 10%", annotation_position="right")
            fig_box.update_yaxes(title_text="Efektivitas Pajak (%)")
            fig_box.update_xaxes(title_text="Segmentasi")
            fig_box.update_layout(
                height=450,
                font=dict(size=10),
                margin=dict(l=50, r=50, t=40, b=50),
                showlegend=False
            )
            st.plotly_chart(fig_box, use_container_width=True)
        except Exception as e:
            st.error(f"Error box chart: {str(e)}")
    else:
        st.warning("Data efektivitas tidak tersedia")

st.markdown("---")

# ========== ROW 3: ANALISIS LANJUTAN ==========
st.markdown('<div class="section-header">🎯 ANALISIS STRATEGIS</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

# Chart 5: Top 10 WP Penyumbang Pajak
with col1:
    st.subheader("Top 10 Wajib Pajak Penyumbang Terbesar")
    if 'NAMA_WP' in df_filtered.columns and 'Total_Pajak_12Bulan' in df_filtered.columns and len(df_filtered) > 0:
        try:
            top_wp = df_filtered.nlargest(min(10, len(df_filtered)), 'Total_Pajak_12Bulan')[['NAMA_WP', 'Total_Pajak_12Bulan']].copy()
            top_wp['Pajak_Miliar'] = top_wp['Total_Pajak_12Bulan'] / 1e9
            top_wp = top_wp.sort_values('Pajak_Miliar', ascending=True)
            
            fig_top = px.bar(
                data_frame=top_wp,
                y='NAMA_WP',
                x='Pajak_Miliar',
                title="10 WP Kontribusi Pajak Tertinggi",
                color='Pajak_Miliar',
                color_continuous_scale='Reds',
                orientation='h'
            )
            fig_top.update_xaxes(title_text="Pajak (Miliar Rp)")
            fig_top.update_yaxes(title_text="Nama WP")
            fig_top.update_layout(
                height=450,
                font=dict(size=9),
                margin=dict(l=150, r=20, t=40, b=50),
                showlegend=False
            )
            st.plotly_chart(fig_top, use_container_width=True)
        except Exception as e:
            st.error(f"Error top WP chart: {str(e)}")
    else:
        st.warning("Data top WP tidak tersedia")

# Chart 6: Distribusi Efektivitas Pajak (Histogram)
with col2:
    st.subheader("Distribusi Tingkat Efektivitas Pajak")
    if 'Efektivitas_Pajak' in df_filtered.columns and len(df_filtered) > 0:
        try:
            fig_hist = px.histogram(
                df_filtered,
                x='Efektivitas_Pajak',
                nbins=25,
                title="Histogram: Sebaran Efektivitas Pajak",
                color_discrete_sequence=['#3498db']
            )
            fig_hist.add_vline(x=10, line_dash="dash", line_color="red", annotation_text="Target 10%", annotation_position="top left")
            fig_hist.add_vline(x=9.5, line_dash="dot", line_color="orange", annotation_text="Ambang Risiko 9.5%", annotation_position="bottom right")
            fig_hist.update_xaxes(title_text="Efektivitas Pajak (%)")
            fig_hist.update_yaxes(title_text="Jumlah WP")
            fig_hist.update_layout(
                height=450,
                font=dict(size=11),
                margin=dict(l=50, r=50, t=40, b=50),
                showlegend=False
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        except Exception as e:
            st.error(f"Error histogram: {str(e)}")
    else:
        st.warning("Data efektivitas tidak tersedia")

st.markdown("---")

# ========== TABEL DETAIL DATA ==========
st.markdown('<div class="section-header">📋 TABEL DETAIL DATA WAJIB PAJAK</div>', unsafe_allow_html=True)

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
        
        # Urutkan
        if sort_by in df_filtered.columns:
            df_display = df_display.sort_values(sort_by, ascending=False, na_position='last')
        
        # Format untuk tampilan
        if 'Total_Omset_12Bulan' in df_display.columns:
            df_display['Omset'] = df_display['Total_Omset_12Bulan'].apply(
                lambda x: f"Rp {x/1e9:.2f}M" if pd.notna(x) else "-"
            )
        if 'Total_Pajak_12Bulan' in df_display.columns:
            df_display['Pajak'] = df_display['Total_Pajak_12Bulan'].apply(
                lambda x: f"Rp {x/1e9:.2f}M" if pd.notna(x) else "-"
            )
        if 'Efektivitas_Pajak' in df_display.columns:
            df_display['Efektivitas'] = df_display['Efektivitas_Pajak'].apply(
                lambda x: f"{x:.2f}%" if pd.notna(x) else "-"
            )
        
        # Pilih kolom untuk ditampilkan
        display_final = [
            'NAMA_WP', 'Kategori', 'Segmentasi', 'Omset', 'Pajak', 'Efektivitas',
            'Label_Risiko' if 'Label_Risiko' in df_display.columns else None
        ]
        display_final = [col for col in display_final if col is not None and col in df_display.columns or col in ['Omset', 'Pajak', 'Efektivitas']]
        
        # Ganti nama kolom untuk tampilan yang lebih rapi
        df_display_final = df_display[['NAMA_WP', 'Kategori', 'Segmentasi', 'Omset', 'Pajak', 'Efektivitas']].copy()
        if 'Label_Risiko' in df_display.columns:
            df_display_final['Label_Risiko'] = df_display['Label_Risiko']
        
        df_display_final.columns = ['Nama WP', 'Kategori', 'Segmentasi', 'Omset', 'Pajak', 'Efektivitas']
        if 'Label_Risiko' in df_display.columns:
            df_display_final['Status Risiko'] = df_display['Label_Risiko']
        
        st.dataframe(
            df_display_final.head(25),
            use_container_width=True,
            height=600,
            hide_index=True
        )
        st.caption(f"📌 Menampilkan 25 dari {len(df_filtered)} WP terpilih | Dapat di-scroll dan di-sort")
        
        # Download button
        csv = df_display_final.to_csv(index=False)
        st.download_button(
            label="📥 Download Data (CSV)",
            data=csv,
            file_name=f"pajak_restoran_tasikmalaya_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error menampilkan tabel: {str(e)}")
        st.info(f"Debug - Kolom yang ada: {df_filtered.columns.tolist()}")
else:
    st.warning("Tidak ada data yang dapat ditampilkan")

st.markdown("---")

# ========== SUMMARY INSIGHTS ==========
st.markdown('<div class="section-header">💡 RINGKASAN WAWASAN UNTUK ATASAN</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **🎯 PRIORITAS UTAMA**
    
    • Fokus intensifikasi pada Segmen **Platinum** (16 WP besar)
    • Target: Peningkatan efektivitas 5%
    • Hasil: +Rp 1.4 Triliun/tahun
    • ROI: <2 bulan
    """)

with col2:
    st.warning("""
    **⚠️ RISIKO YANG TERDETEKSI**
    
    • 87% WP efektivitas <9.5%
    • Indikasi: Pelaporan rendah
    • Diperlukan: Audit tertarget
    • Action: Edukasi + e-reporting
    """)

with col3:
    st.success("""
    **✅ PENCAPAIAN POSITIF**
    
    • Efektivitas: 11.65% (>10%)
    • Data quality: 99.2% lengkap
    • Akurasi model: 85%
    • Status: On Track 2026
    """)

st.markdown("---")

# ========== FOOTER ==========
st.markdown("""
    <div style='text-align: center; padding: 20px; color: #888888; font-size: 12px;'>
    <b>Dasbor Analisis Pajak Restoran Tasikmalaya</b><br>
    PySpark MLlib | K-Means Clustering | Logistic Regression<br>
    Data: Oktober 2025 | Update: Real-time dari GitHub<br>
    <br>
    Disusun untuk: Bapenda Kota Tasikmalaya<br>
    Program Studi: Magister Informatika (Konsentrasi Data Science) UII<br>
    Tahun: 2026
    </div>
""", unsafe_allow_html=True)
