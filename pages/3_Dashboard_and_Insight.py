import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D 
from matplotlib import cm
from model import gabung_final, rekomendasi_produk

# Konfigurasi halaman
st.set_page_config(
    page_title="Qaraa Segmentation App",
    page_icon="assets/favicon.png",
    layout="wide"
)

with st.sidebar:
    st.image("assets/favicon.png", width=150)
    st.markdown("Qaraa Segmentation App")

st.set_page_config(page_title="Customer Dashboard", layout="wide")
st.title("📊 Customer Dashboard & Rekomendasi Produk")



# Validasi session
if "data_bersih" not in st.session_state or "df_clustered" not in st.session_state:
    st.warning("⚠️ Silakan selesaikan proses RFM & Clustering terlebih dahulu.")
    st.stop()

# Ambil data dari session
df_clean = st.session_state["data_bersih"]
df_clustered = st.session_state["df_clustered"]

# Gabungkan data akhir
df_final = gabung_final(df_clean, df_clustered)

# Tambahkan Segmentasi & Strategi berdasarkan Cluster
cluster_rekomendasi = {
    0: ("Pelanggan Baru", "Edukasi produk & penawaran awal"),
    1: ("Pelanggan Loyal", "Program loyalitas & diskon bundling"),
    2: ("High Spender", "Produk premium, upsell & eksklusif"),
    3: ("Pelanggan Tidak Aktif", "Kampanye reaktivasi & reminder")
}

df_segmentasi = pd.DataFrame([
    {"Cluster": k, "Segmentasi": v[0], "Strategi": v[1]}
    for k, v in cluster_rekomendasi.items()
])

df_final = df_final.merge(df_segmentasi, on="Cluster", how="left")

# ==========================================
# ✅ Bersihkan data → Ambil hanya transaksi terakhir tiap pelanggan
df_latest = (
    df_final
    .sort_values("Order_date")
    .groupby(["Customer_name", "Customer_id"], as_index=False)
    .tail(1)
    .sort_values("Cluster")
    .reset_index(drop=True)
)
# ==========================================

# Tampilkan data bersih per customer (1 baris per pelanggan)
st.markdown("---")
st.subheader("📌 Data Terakhir Order per Customer")
st.dataframe(df_latest.head(20), use_container_width=True)

# Tampilkan daftar pelanggan bernilai tinggi (cluster terbaik)
st.markdown("---")
top_cluster = df_clustered.groupby('Cluster')['Total_Transaksi'].mean().idxmax()
df_high_value = df_latest[df_latest['Cluster'] == top_cluster]
st.subheader(f"🏆 Pelanggan Bernilai Tinggi (Cluster {top_cluster})")
st.dataframe(
    df_high_value[['Customer_name', 'Customer_id', 'Order_date', 'Total_Transaksi', 'Product_Name']],
    use_container_width=True
)

# Rekomendasi produk
st.markdown("---")
st.subheader("🎯 Rekomendasi Produk Tiap Cluster")
df_rekomendasi = rekomendasi_produk(df_final)
st.dataframe(df_rekomendasi, use_container_width=True)

# Tabel Segmentasi
st.markdown("---")
st.subheader("🧭 Segmentasi & Strategi per Cluster")
st.dataframe(df_segmentasi, use_container_width=True)

# Visualisasi jumlah pelanggan per cluster
st.markdown("---")
st.subheader("👥 Jumlah Pelanggan per Cluster")
fig1, ax1 = plt.subplots()
sns.countplot(data=df_latest, x='Cluster', palette='viridis', ax=ax1)
ax1.set_title("Distribusi Pelanggan per Cluster")
st.pyplot(fig1)

# Visualisasi rata-rata transaksi per cluster
st.markdown("---")
st.subheader("💰 Rata-rata Transaksi per Cluster")
fig2, ax2 = plt.subplots()
sns.barplot(
    data=df_latest,
    x='Cluster',
    y='Total_Transaksi',
    estimator='mean',
    ci=None,
    palette='rocket',
    ax=ax2
)
ax2.set_title("Rata-Rata Total Transaksi per Cluster")
st.pyplot(fig2)


# Ambil data RFM dan Cluster untuk visualisasi 3D
st.markdown("---")
rfm_3d = df_clustered.copy()
st.subheader("🌐 Visualisasi 3D - KMeans Clustering")

fig3 = plt.figure(figsize=(10, 7))
ax = fig3.add_subplot(111, projection='3d')

# Plot titik-titik pelanggan
scatter = ax.scatter(
    rfm_3d['Recency'],
    rfm_3d['Frequency'],
    rfm_3d['Total_Transaksi'],
    c=rfm_3d['Cluster'],
    cmap='tab10',
    s=60,
    alpha=0.8
)

# Label sumbu
ax.set_xlabel('Recency (Hari)')
ax.set_ylabel('Frequency (Jumlah Order)')
ax.set_zlabel('Total Transaksi (Rp)')
ax.set_title('📊 Visualisasi 3D Clustering Pelanggan')

# Tambahkan legenda cluster
legend_labels = [f"Cluster {i}" for i in sorted(rfm_3d['Cluster'].unique())]
legend_handles = [plt.Line2D([0], [0], marker='o', color='w',
                             label=label,
                             markerfacecolor=cm.tab10(i / 10), markersize=10)
                  for i, label in enumerate(legend_labels)]
ax.legend(handles=legend_handles, title='Cluster', loc='upper right')

# Tampilkan di Streamlit
st.pyplot(fig3)
                            

# Export CSV
st.subheader("⬇️ Unduh Data Akhir (1 baris per customer)")
df_latest.to_csv("assets/final_clustered_latest.csv", index=False)
with open("assets/final_clustered_latest.csv", "rb") as f:
    st.download_button(
        "📥 Download Data Customer Terakhir Order",
        f,
        file_name="final_clustered_latest.csv",
        mime="text/csv"
    )
