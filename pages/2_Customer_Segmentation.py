import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman
st.set_page_config(
    page_title="Qaraa Segmentation App",
    page_icon="assets/favicon.png",
    layout="wide"
)

with st.sidebar:
    st.image("assets/favicon.png", width=150)
    st.markdown("Qaraa Segmentation App")


st.set_page_config(page_title="Customer Clustering Insight", layout="wide")
st.title("📈 Customer Clustering Insight")

# Validasi session
if "df_clustered" not in st.session_state or "data_bersih" not in st.session_state:
    st.warning("⚠️ Silakan jalankan proses Clustering terlebih dahulu.")
    st.stop()

df_clustered = st.session_state["df_clustered"]
df_clean = st.session_state["data_bersih"]

# Ringkasan Clustering
st.subheader("📊 Ringkasan Statistik Cluster Pelanggan")
summary_stats = df_clustered.groupby("Cluster").agg({
    "Recency": ["mean", "median", "nunique"],
    "Frequency": ["mean", "median", "nunique"],
    "Total_Transaksi": ["mean", "median", "nunique"]
}).round(2)
summary_stats.columns = ['_'.join(col) for col in summary_stats.columns]
st.dataframe(summary_stats, use_container_width=True)

# Komposisi pelanggan per cluster
st.markdown("---")
st.subheader("📌 Komposisi Pelanggan per Cluster")
cluster_counts = df_clustered['Cluster'].value_counts().sort_index()
cluster_labels = [f"Cluster {i}" for i in cluster_counts.index]
fig_pie, ax_pie = plt.subplots()
ax_pie.pie(
    cluster_counts,
    labels=cluster_labels,
    autopct='%1.1f%%',
    startangle=140,
    colors=sns.color_palette("tab10")
)
ax_pie.axis("equal")
st.pyplot(fig_pie)

# Visualisasi distribusi RFM per cluster
st.markdown("---")
st.subheader("📊 Distribusi RFM per Cluster")
col1, col2, col3 = st.columns(3)

with col1:
    fig1, ax1 = plt.subplots()
    sns.boxplot(data=df_clustered, x="Cluster", y="Recency", palette="Pastel1", ax=ax1)
    ax1.set_title("Distribusi Recency per Cluster")
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots()
    sns.boxplot(data=df_clustered, x="Cluster", y="Frequency", palette="Pastel2", ax=ax2)
    ax2.set_title("Distribusi Frequency per Cluster")
    st.pyplot(fig2)

with col3:
    fig3, ax3 = plt.subplots()
    sns.boxplot(data=df_clustered, x="Cluster", y="Total_Transaksi", palette="Set3", ax=ax3)
    ax3.set_title("Distribusi Total Transaksi per Cluster")
    st.pyplot(fig3)

# Detail pelanggan per cluster
st.markdown("---")
st.subheader("📋 Detail Pelanggan per Cluster")
selected_cluster = st.selectbox("Pilih Cluster", sorted(df_clustered['Cluster'].unique()))
df_filtered = df_clustered[df_clustered["Cluster"] == selected_cluster]
st.dataframe(df_filtered, use_container_width=True)

# Export file clustering utama
st.markdown("---")
st.subheader("⬇️ Unduh Data Clustering RFM")
df_clustered.to_csv("assets/rfm_customer_cluster.csv", index=False)
with open("assets/rfm_customer_cluster.csv", "rb") as f:
    st.download_button(
        "📥 Download RFM Clustered Dataset",
        f,
        file_name="rfm_customer_cluster.csv",
        mime="text/csv"
    )

# =============================================
# ✅ Nama & Produk yang Dibeli per Segment RFM
# =============================================
st.markdown("---")
st.subheader("🧾 Nama & Produk Pelanggan Berdasarkan Segmentasi RFM")

# Pastikan ID sebagai string
df_clean['Customer_id'] = df_clean['Customer_id'].astype(str)
df_clustered['Customer_id'] = df_clustered['Customer_id'].astype(str)

# Fungsi segmentasi
def segment_customer(row):
    r, f = row['Recency'], row['Frequency']
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

# Tambahkan kolom Segment
df_clustered['Segment'] = df_clustered.apply(segment_customer, axis=1)

# Gabungkan nama dan produk
df_rfm_full = df_clustered.merge(
    df_clean[['Customer_id', 'Customer_name', 'Product_Name']],
    on='Customer_id',
    how='left'
).drop_duplicates(subset=['Customer_id', 'Segment', 'Product_Name'])

# Ambil kolom relevan
df_customer_cluster_detail = df_rfm_full[[
    'Customer_id', 'Customer_name', 'Segment', 'Product_Name',
    'Recency', 'Frequency', 'Total_Transaksi'
]].sort_values(by='Segment')

# Tampilkan
st.dataframe(df_customer_cluster_detail, use_container_width=True)

# Tombol download data segment
df_customer_cluster_detail.to_csv("assets/rfm_customer_segmented.csv", index=False)
with open("assets/rfm_customer_segmented.csv", "rb") as f:
    st.download_button(
        "📥 Download Segmentasi RFM + Produk",
        f,
        file_name="rfm_customer_segmented.csv",
        mime="text/csv"
    )
