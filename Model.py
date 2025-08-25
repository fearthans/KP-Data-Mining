import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
import numpy as np



# 1. Data Cleaning
def bersihkan_data(df):
    df['Price_clean'] = (
        df['Price'].astype(str)
        .str.replace('Rp', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.strip()
    )
    df['Price_clean'] = pd.to_numeric(df['Price_clean'], errors='coerce')
    df['Order_id'] = df['Order_id'].fillna(method='ffill')
    df['Order_date'] = pd.to_datetime(df['Order_date'], errors='coerce')
    df = df.dropna(subset=['Customer_id', 'Order_date', 'Price_clean']).copy()
    df['Customer_id'] = df['Customer_id'].astype(float).astype(int).astype(str)  # Hilangkan .0
    df['Total_Transaksi'] = df['Quantity'] * df['Price_clean']
    df = df[df['Total_Transaksi'] > 0]
    df.to_csv("assets/data_bersih.csv", index=False)
    return df


# 2. Hitung RFM
def hitung_rfm(df_clean):
    ref_date = df_clean['Order_date'].max()
    df_agg = df_clean.groupby('Customer_id').agg({
        'Order_id': 'count',
        'Total_Transaksi': 'sum',
        'Order_date': 'max'
    }).reset_index()

    df_agg.rename(columns={
        'Order_id': 'Frequency',
        'Order_date': 'Last_Order_Date'
    }, inplace=True)

    df_agg['Recency'] = (ref_date - df_agg['Last_Order_Date']).dt.days
    df_agg['Avg_Transaction'] = (df_agg['Total_Transaksi'] / df_agg['Frequency']).fillna(0).round(0).astype(int)

    df_agg.to_csv("assets/rfm_result.csv", index=False)
    return df_agg


# 3. Clustering KMeans
def lakukan_clustering(df_agg, n_clusters):
    features = df_agg[['Frequency', 'Total_Transaksi', 'Recency', 'Avg_Transaction']]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_agg['Cluster'] = kmeans.fit_predict(X_scaled)

    centroids_scaled = kmeans.cluster_centers_
    centroids = scaler.inverse_transform(centroids_scaled)

    db_index = davies_bouldin_score(X_scaled, df_agg['Cluster'])
    sil_score = silhouette_score(X_scaled, df_agg['Cluster'])

    return df_agg, centroids, db_index, sil_score, scaler, X_scaled


# 4. Evaluasi Elbow (range 1-10)
def elbow_method(X_scaled, max_k=10):
    wcss = []
    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        wcss.append(kmeans.inertia_)
    return list(range(1, max_k + 1)), wcss


# 5. Evaluasi DBI & Silhouette dalam tabel (multi K)
def evaluasi_multi_k(X_scaled, k_range):
    dbi_results, sil_results = [], []

    for k in k_range:
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = model.fit_predict(X_scaled)
        dbi = davies_bouldin_score(X_scaled, labels)
        sil = silhouette_score(X_scaled, labels)
        dbi_results.append([k, dbi])
        sil_results.append([k, sil])

    return pd.DataFrame(dbi_results, columns=['Jumlah Cluster', 'Davies-Bouldin Index']), \
           pd.DataFrame(sil_results, columns=['Jumlah Cluster', 'Silhouette Score'])


# 6. Gabung ke data akhir + customer name
def gabung_final(df_clean, df_clustered, df_customer=None):
    df_clean['Customer_id'] = df_clean['Customer_id'].astype(str)
    df_clustered['Customer_id'] = df_clustered['Customer_id'].astype(str)

    df_final = df_clean.merge(df_clustered[['Customer_id', 'Cluster']], on='Customer_id', how='left')

    if df_customer is not None:
        df_customer['Customer_id'] = df_customer['Customer_id'].astype(str)
        df_final = df_final.merge(df_customer[['Customer_id', 'Customer_name']], on='Customer_id', how='left')

    df_final.to_csv("assets/final_clustered.csv", index=False)
    return df_final


# 7. Rekomendasi produk per cluster
def rekomendasi_produk(df_final, simpan=True):
    rekom = (
        df_final
        .groupby(['Cluster', 'Product_Name'])['Total_Transaksi']
        .sum()
        .reset_index()
        .sort_values(['Cluster', 'Total_Transaksi'], ascending=[True, False])
    )
    top_produk = rekom.groupby('Cluster').head(1).reset_index(drop=True)

    if simpan:
        top_produk.to_csv("assets/hasil_rekomendasi.csv", index=False)

    return top_produk


