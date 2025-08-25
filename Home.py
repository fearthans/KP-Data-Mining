import streamlit as st
import pandas as pd
from model import bersihkan_data

# Konfigurasi halaman
st.set_page_config(
    page_title="Qaraa Segmentation App",
    page_icon="assets/favicon.png",
    layout="wide"
)

# Load external CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("assets/style_qaraa.css")

# Sidebar
with st.sidebar:
    st.image("assets/favicon.png", width=150)
    st.markdown("**Qaraa Segmentation App**")

# Header
st.markdown("<h1>👋 Selamat Datang!</h1>", unsafe_allow_html=True)
st.markdown("<p class='small-text'>Aplikasi ini membantu mengelompokkan pelanggan berdasarkan pola transaksi menggunakan K-Means Clustering.</p>", unsafe_allow_html=True)

# Divider
st.markdown("<hr>", unsafe_allow_html=True)

# Upload File Section
uploaded_file = st.file_uploader("📂 Upload file transaksi pelanggan (format: .csv)", type=["csv"])

st.markdown("### 📥 Contoh Format File Transaksi yang Diterima")

with open("assets/sample_transaksi.csv", "rb") as file:
    st.download_button(
        label="📥 Download Contoh File CSV",
        data=file,
        file_name="contoh_transaksi.csv",
        mime="text/csv"
    )

st.caption("Gunakan file ini sebagai referensi format untuk mengupload data pelanggan.")

# Hasil Upload dan Pembersihan
if uploaded_file:
    try:
        df_raw = pd.read_csv(uploaded_file)
        df_clean = bersihkan_data(df_raw)

        # Simpan ke session_state
        st.session_state["data_awal"] = df_raw
        st.session_state["data_bersih"] = df_clean

        st.success("✅ File berhasil diupload dan data berhasil dibersihkan!")
        st.markdown("👉 Silakan lanjut ke menu **RFM Analysis** di sidebar untuk langkah selanjutnya.")

        with st.expander("🔍 Lihat Data Asli (Raw)"):
            st.dataframe(df_raw, use_container_width=True, height=400)
            st.markdown(f"📦 Jumlah data awal: **{len(df_raw)}** baris")

        with st.expander("✅ Lihat Data Bersih (Siap Olah)"):
            st.dataframe(df_clean, use_container_width=True, height=400)
            st.markdown(f"🧹 Jumlah data setelah dibersihkan: **{len(df_clean)}** baris")
            st.markdown(f"❌ Data yang dibuang: **{len(df_raw) - len(df_clean)}** baris")

    except Exception as e:
        st.error(f"Terjadi kesalahan saat membaca file: {e}")
else:
    st.warning("⚠️ Silakan upload file CSV terlebih dahulu.")

# Divider
st.markdown("<hr>", unsafe_allow_html=True)

# Alur Analisis
st.markdown("""
<div class="qaraa-card">
    <div class="qaraa-title">🚀 Alur Analisis</div>
    <div class="qaraa-subtext">
        <ol>
            <li><b>RFM Analysis</b> – Hitung Recency, Frequency, dan Monetary</li>
            <li><b>Clustering</b> – Segmentasi pelanggan menggunakan K-Means + evaluasi DBI & Silhouette</li>
            <li><b>Customer Segmentation</b> – Tampilkan nama pelanggan, produk, dan segmen</li>
            <li><b>Dashboard & Insight</b> – Visualisasi & ringkasan hasil segmentasi</li>
        </ol>
    </div>
</div>
""", unsafe_allow_html=True)
