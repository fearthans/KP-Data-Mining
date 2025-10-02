import streamlit as st
import pandas as pd
from Model import bersihkan_data
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="Qaraa Segmentation App",
    page_icon="assets/favicon.png",
    layout="wide"
)

# Load CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/style_qaraa.css")

# Sidebar
with st.sidebar:
    st.image("assets/favicon.png", width=150)
    st.markdown("**Qaraa Segmentation App**")

# Header
st.markdown("<h1 style='font-size: 48px;'>👋 Selamat Datang!</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 22px;'>Aplikasi ini membantu menganalisis pelanggan dengan pendekatan RFM (Recency, Frequency, Monetary)</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================================
# Upload File Section
# ==========================================================
st.subheader("📂 Data Transaksi Pelanggan")

uploaded_file = st.file_uploader("Upload file transaksi (CSV)", type=["csv"], key="upload_csv")

# Tambahkan opsi dataset internal di bawah upload
st.markdown("#### Atau gunakan dataset internal:")
INTERNAL_PATH = os.path.join("assets", "DATASET PT. KREASI PUTRA HOTAMA 2025 - hasil_merge.csv")
use_internal = st.button("📄 Pakai dataset: DATASET PT. KREASI PUTRA HOTAMA 2025 - hasil_merge.csv")

st.caption("Gunakan salah satu: upload file CSV Anda, **atau** klik tombol untuk memakai dataset internal.")

# Contoh format file
st.markdown("### 📥 Contoh Format File Transaksi yang Diterima")
with open("assets/sample_transaksi.csv", "rb") as file:
    st.download_button(
        label="📥 Download Contoh File CSV",
        data=file,
        file_name="contoh_transaksi.csv",
        mime="text/csv"
    )
    
# ==========================================================
# Proses Data: Upload ATAU Dataset Internal
# ==========================================================
df_raw = None
source_label = None

if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file)
        source_label = f"📤 Sumber: Upload ({uploaded_file.name})"
    except Exception as e:
        st.error(f"Gagal membaca file upload: {e}")

elif use_internal:
    if os.path.exists(INTERNAL_PATH):
        try:
            df_raw = pd.read_csv(INTERNAL_PATH)
            source_label = f"📄 Sumber: Dataset Internal (DATASET PT. KREASI PUTRA HOTAMA 2025 - hasil_merge.csv)"
        except Exception as e:
            st.error(f"Gagal membaca dataset internal: {e}")
    else:
        st.error("File dataset internal tidak ditemukan di folder assets/. Pastikan nama & lokasi file benar.")

# ==========================================================
# Tampilkan Hasil & Simpan ke Session
# ==========================================================
if df_raw is not None:
    try:
        df_clean = bersihkan_data(df_raw)

        st.session_state["data_awal"] = df_raw
        st.session_state["data_bersih"] = df_clean

        st.success("✅ Data berhasil dimuat dan dibersihkan!")
        if source_label:
            st.caption(source_label)
        st.markdown("👉 Lanjut ke menu **RFM Analysis** dan **RFM Insights** di sidebar.")

        with st.expander("🔍 Lihat Data Asli (Raw)"):
            st.dataframe(df_raw, use_container_width=True, height=400)
            st.markdown(f"📦 Jumlah data awal: **{len(df_raw)}** baris")

        with st.expander("✅ Lihat Data Bersih (Siap Olah)"):
            st.dataframe(df_clean, use_container_width=True, height=400)
            st.markdown(f"🧹 Jumlah data setelah dibersihkan: **{len(df_clean)}** baris")
            st.markdown(f"❌ Data yang dibuang: **{len(df_raw) - len(df_clean)}** baris")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membersihkan data: {e}")
else:
    st.info("Silakan **upload CSV** atau **pakai dataset internal** untuk mulai.")

st.markdown("<hr>", unsafe_allow_html=True)

# ==========================================================
# Alur Analisis
# ==========================================================
st.markdown("""
<div class="qaraa-card">
    <div class="qaraa-title">🚀 Alur Analisis (RFM)</div>
    <div class="qaraa-subtext">
        <ol>
            <li><b>RFM Analysis</b> – Hitung Recency, Frequency, dan Monetary</li>
            <li><b>RFM Insights</b> – Visualisasi, segmentasi RFM sederhana, dan ringkasan</li>
        </ol>
    </div>
</div>
""", unsafe_allow_html=True)
