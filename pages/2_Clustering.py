import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from model import hitung_rfm, lakukan_clustering, elbow_method, evaluasi_multi_k

# Konfigurasi halaman
st.set_page_config(
    page_title="Qaraa Segmentation App",
    page_icon="assets/favicon.png",
    layout="wide"
)

with st.sidebar:
    st.image("assets/favicon.png", width=150)
    st.markdown("Qaraa Segmentation App")

st.set_page_config(page_title="Clustering Pelanggan", layout="wide")
st.title("🔍 Clustering Pelanggan - KMeans")

# Validasi session
if "data_bersih" not in st.session_state:
    st.warning("⚠️ Silakan upload data terlebih dahulu di halaman Home.")
    st.stop()

# Ambil dan proses data
df_clean = st.session_state["data_bersih"]
df_rfm = hitung_rfm(df_clean)

# Sidebar: Pilih jumlah cluster
st.sidebar.header("⚙️ Pengaturan Cluster")
k = st.sidebar.slider("Pilih jumlah cluster", min_value=2, max_value=10, value=4)


# Proses clustering
df_clustered, centroids, dbi, sil, scaler, X_scaled = lakukan_clustering(df_rfm, k)
st.session_state["df_clustered"] = df_clustered

# Tabel hasil clustering
st.subheader("📌 Tabel Hasil Clustering (Keseluruhan)")

# Tampilkan seluruh data, scroll otomatis
st.dataframe(
    df_clustered,
    use_container_width=True,
    height=500 
)

# Visualisasi clustering
st.markdown("---")
st.subheader("📊 Visualisasi Cluster")
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(
    data=df_clustered,
    x='Total_Transaksi',
    y='Avg_Transaction',
    hue='Cluster',
    palette='tab10',
    s=100,
    ax=ax
)
ax.scatter(
    centroids[:, 1], centroids[:, 3],
    marker='X', s=200, color='white', edgecolor='black', label='Centroids'
)
ax.set_title("Cluster Pelanggan berdasarkan Pola Transaksi")
ax.legend()
st.pyplot(fig)

# Elbow Method
st.markdown("---")
st.subheader("📉 Elbow Method")
range_k, wcss = elbow_method(X_scaled)
fig2, ax2 = plt.subplots()
ax2.plot(range_k, wcss, marker='o')
ax2.set_title("Elbow Method")
ax2.set_xlabel("Jumlah Cluster (k)")
ax2.set_ylabel("WCSS")
st.pyplot(fig2)


# Evaluasi Clustering
st.markdown("---")
st.subheader("📊 Evaluasi Clustering")
st.markdown(f"- **Davies-Bouldin Index (k={k})**: `{dbi:.4f}`")
st.markdown(f"- **Silhouette Score (k={k})**: `{sil:.4f}`")

# Tabel Evaluasi Tambahan
st.markdown("---")
st.subheader("📊 Tabel Evaluasi Tambahan")
range_custom = st.slider("Range jumlah cluster untuk evaluasi", 2, 10, (2, 6))
k_range = list(range(range_custom[0], range_custom[1] + 1))
df_dbi, df_sil = evaluasi_multi_k(X_scaled, k_range)

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Davies-Bouldin Index**")
    st.dataframe(df_dbi, use_container_width=True)
with col2:
    st.markdown("**Silhouette Score**")
    st.dataframe(df_sil, use_container_width=True)

# Tombol download
df_clustered.to_csv("assets/rfm_clustered.csv", index=False)
with open("assets/rfm_clustered.csv", "rb") as f:
    st.download_button(
        "📥 Download Data Clustering",
        f,
        file_name="rfm_clustered.csv",
        mime="text/csv"
    )
