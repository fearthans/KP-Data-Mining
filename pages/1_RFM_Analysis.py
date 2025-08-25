import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from model import hitung_rfm

# Konfigurasi halaman
st.set_page_config(
    page_title="Qaraa Segmentation App",
    page_icon="assets/favicon.png",
    layout="wide"
)

with st.sidebar:
    st.image("assets/favicon.png", width=150)
    st.markdown("Qaraa Segmentation App")

st.set_page_config(page_title="RFM Analysis", layout="wide")
st.title("📦 RFM Analysis")

# Validasi data
if "data_bersih" not in st.session_state:
    st.warning("⚠️ Silakan upload data terlebih dahulu di halaman Home.")
    st.stop()

# Ambil data bersih
df_clean = st.session_state["data_bersih"]

# Hitung RFM
df_rfm = hitung_rfm(df_clean)

st.success("✅ Data berhasil dihitung RFM-nya.")

# Tampilkan tabel RFM
st.subheader("📟 Data RFM")
st.dataframe(df_rfm.head(15), use_container_width=True)

# Info tambahan
st.markdown(f"📌 Total pelanggan tersegmentasi: **{df_rfm.shape[0]} pelanggan**")

# Tombol download
st.markdown("---")
st.subheader("⬇️ Unduh Data")

col1, col2 = st.columns(2)
with col1:
    with open("assets/rfm_result.csv", "rb") as f:
        st.download_button(
            "📥 Download RFM (CSV)",
            f,
            file_name="rfm_result.csv",
            mime="text/csv"
        )
with col2:
    with open("assets/data_bersih.csv", "rb") as f:
        st.download_button(
            "📥 Download Data Bersih (CSV)",
            f,
            file_name="data_bersih.csv",
            mime="text/csv"
        )



st.markdown("---")
st.subheader("📈 Analisis RFM Lebih Lanjut")

# Rename dulu agar mudah dipahami
df_rfm_analisis = df_rfm.copy()
df_rfm_analisis.rename(columns={
    'Recency': 'day_since_last_order',
    'Frequency': 'order_cnt',
    'Total_Transaksi': 'total_order_value'
}, inplace=True)

# (Opsional) Tambah fitur PCT unik produk kalau kamu punya
# df_rfm_analisis['pct_unique'] = ...

# Binning Segmentasi RFM sederhana
def assign_segment(row):
    if row['day_since_last_order'] <= 30 and row['order_cnt'] >= 4:
        return "Champion"
    elif row['order_cnt'] >= 3:
        return "Loyal Customers"
    elif row['order_cnt'] >= 2 and row['day_since_last_order'] <= 60:
        return "Potential Loyalists"
    elif row['order_cnt'] >= 2 and row['day_since_last_order'] > 90:
        return "Can't Lose Them"
    elif row['order_cnt'] == 1 and row['day_since_last_order'] > 90:
        return "At Risk"
    elif row['day_since_last_order'] > 60 and row['order_cnt'] == 1:
        return "About to Sleep"
    elif row['day_since_last_order'] <= 30 and row['order_cnt'] == 1:
        return "New Customers"
    elif row['day_since_last_order'] <= 90 and row['order_cnt'] == 1:
        return "Promising"
    elif row['order_cnt'] <= 2:
        return "Need Attention"
    else:
        return "Others"

df_rfm_analisis['Segment'] = df_rfm_analisis.apply(assign_segment, axis=1)

# Simpan untuk kebutuhan lainnya
st.session_state['df_rfm_segment'] = df_rfm_analisis

# Hitung metrik deskriptif per segmen
segment_stats = df_rfm_analisis.groupby('Segment').agg(
    Customer_Count=('Customer_id', 'nunique'),
    Mean_Days=('day_since_last_order', 'mean'),
    Median_Days=('day_since_last_order', 'median'),
    Mean_Orders=('order_cnt', 'mean'),
    Median_Orders=('order_cnt', 'median'),
    Mean_Value=('total_order_value', 'mean'),
    Median_Value=('total_order_value', 'median')
).sort_values(by='Customer_Count', ascending=False).reset_index()

# Tampilkan tabel
st.dataframe(segment_stats, use_container_width=True)

# Optional: Simpan CSV
segment_stats.to_csv("assets/segment_analysis.csv", index=False)
with open("assets/segment_analysis.csv", "rb") as f:
    st.download_button("📥 Download Tabel Segmentasi RFM", f, file_name="segment_analysis.csv", mime="text/csv")



st.markdown("---")
st.subheader("📊 RFM Segment Analysis")

# Buat salinan dari df_rfm
df_rfm_analisis = df_rfm.copy()
df_rfm_analisis.rename(columns={
    'Recency': 'day_since_last_order',
    'Frequency': 'order_cnt',
    'Total_Transaksi': 'total_order_value'
}, inplace=True)

# Tambahkan 'pct_unique' dummy jika belum ada
if 'pct_unique' not in df_rfm_analisis.columns:
    np.random.seed(42)
    df_rfm_analisis['pct_unique'] = np.random.uniform(1, 30, size=len(df_rfm_analisis)).round(1)

# RFM Segmentation Rule (Versi gambar)
def segment_customer(row):
    r, f = row['day_since_last_order'], row['order_cnt']
    if r <= 30 and f >= 10:
        return "01-Champion"
    elif f >= 7:
        return "02-Loyal Customers"
    elif r <= 60 and f >= 3:
        return "03-Potential Loyalists"
    elif r > 90 and f >= 8:
        return "04-Can't Lose Them"
    elif r > 60 and f <= 3:
        return "05-Need Attention"
    elif r <= 30 and f == 1:
        return "06-New Customers"
    elif r <= 90 and f == 1:
        return "07-Promising"
    elif r > 90 and f <= 4:
        return "08-At Risk"
    elif r > 60 and f <= 2:
        return "09-About to Sleep"
    else:
        return "10-Hibernating"

df_rfm_analisis['segment'] = df_rfm_analisis.apply(segment_customer, axis=1)

# Hitung statistik
segment_table = df_rfm_analisis.groupby('segment').agg({
    'Customer_id': 'nunique',
    'day_since_last_order': ['mean', 'median'],
    'order_cnt': ['mean', 'median'],
    'total_order_value': ['mean', 'median'],
    'pct_unique': ['mean', 'median']
}).reset_index()

# Rename kolom
segment_table.columns = ['segment', 'nunique',
                         'day_since_last_order_mean', 'day_since_last_order_median',
                         'order_cnt_mean', 'order_cnt_median',
                         'total_order_value_mean', 'total_order_value_median',
                         'pct_unique_mean', 'pct_unique_median']

# Tampilkan Tabel
st.dataframe(segment_table.style.format({
    'day_since_last_order_mean': '{:.2f}', 'day_since_last_order_median': '{:.0f}',
    'order_cnt_mean': '{:.2f}', 'order_cnt_median': '{:.0f}',
    'total_order_value_mean': 'Rp {:,.0f}', 'total_order_value_median': 'Rp {:,.0f}',
    'pct_unique_mean': '{:.1f}', 'pct_unique_median': '{:.1f}',
}), use_container_width=True)

# Download CSV
segment_table.to_csv("assets/rfm_segment_summary.csv", index=False)
with open("assets/rfm_segment_summary.csv", "rb") as f:
    st.download_button("📥 Download RFM Segment Table", f, file_name="rfm_segment_summary.csv", mime="text/csv")

# ========================
# Visualisasi Treemap 📦
# ========================
st.markdown("---")
st.subheader("🗺️ Visualisasi Segmentasi Pelanggan (Treemap)")

# Hitung jumlah per segment
segment_size = df_rfm_analisis['segment'].value_counts().reset_index()
segment_size.columns = ['segment', 'customer_count']

# Hitung total & persentase
total_customer = segment_size['customer_count'].sum()
segment_size['percent'] = (segment_size['customer_count'] / total_customer * 100).round(1)
segment_size['label_full'] = segment_size.apply(
    lambda row: f"{row['segment']} ({row['customer_count']} | {row['percent']}%)", axis=1
)

# label segmen unik sebagai kategori warna 
segment_size['color'] = segment_size['segment']

# warna unik per segmen
color_palette = px.colors.qualitative.Set3  # Atau gunakan Set1, Pastel, Dark, dll

fig = px.treemap(
    segment_size,
    path=['label_full'],
    values='customer_count',
    color='color',
    color_discrete_sequence=color_palette,
    title="Proporsi Pelanggan per Segment"
)

fig.update_traces(textinfo="label+value+percent entry")
fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
st.plotly_chart(fig, use_container_width=True)