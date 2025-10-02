import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="RFM Insights",
    page_icon="assets/favicon.png",
    layout="wide"
)

with st.sidebar:
    st.image("assets/favicon.png", width=150)
    st.markdown("Qaraa Segmentation App")

st.title("📊 RFM Insights")

# =====================
# Validasi session
# =====================
if "data_bersih" not in st.session_state:
    st.warning("⚠️ Silakan hitung RFM terlebih dahulu (menu RFM Analysis).")
    st.stop()

if "df_rfm_segment" not in st.session_state:
    st.warning("⚠️ Belum ada segmentasi RFM. Silakan buka menu RFM Analysis terlebih dahulu.")
    st.stop()

df_clean: pd.DataFrame = st.session_state["data_bersih"].copy()
df_rfm_seg: pd.DataFrame = st.session_state["df_rfm_segment"].copy()

# Pastikan kolom nama tersedia
if "Customer_name" not in df_clean.columns:
    df_clean["Customer_name"] = np.nan

# Satukan nama ke seluruh df_rfm_seg agar konsisten dipakai di semua komponen
df_names = df_clean[["Customer_id", "Customer_name"]].drop_duplicates()
df_rfm_seg = df_rfm_seg.merge(df_names, on="Customer_id", how="left")

# =====================
# Ringkasan Umum RFM
# =====================
st.subheader("📌 Ringkasan RFM")

total_pelanggan = df_rfm_seg["Customer_id"].nunique()
avg_freq = df_rfm_seg["order_cnt"].mean()
avg_monetary = df_rfm_seg["total_order_value"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Pelanggan", f"{total_pelanggan:,}")
col2.metric("Rata-rata Frequency", f"{avg_freq:.2f}")
col3.metric("Rata-rata Monetary", f"Rp {avg_monetary:,.0f}")

# =====================
# Distribusi RFM
# =====================
st.markdown("---")
st.subheader("📈 Distribusi Recency / Frequency / Monetary")

c1, c2, c3 = st.columns(3)

with c1:
    fig_r = px.histogram(
        df_rfm_seg, x="day_since_last_order", nbins=30, title="Distribusi Recency (hari)"
    )
    st.plotly_chart(fig_r, use_container_width=True)

with c2:
    fig_f = px.histogram(
        df_rfm_seg, x="order_cnt", nbins=30, title="Distribusi Frequency (jumlah pesanan)"
    )
    st.plotly_chart(fig_f, use_container_width=True)

with c3:
    fig_m = px.histogram(
        df_rfm_seg, x="total_order_value", nbins=30, title="Distribusi Monetary (Rp)"
    )
    st.plotly_chart(fig_m, use_container_width=True)

# =====================
# Segment Leaderboard
# =====================
st.markdown("---")
st.subheader("🏆 Segment Leaderboard")

seg_leader = (
    df_rfm_seg
    .groupby("Segment")
    .agg(
        Customer_Count=("Customer_id", "nunique"),
        Avg_Freq=("order_cnt", "mean"),
        Avg_Monetary=("total_order_value", "mean"),
        Total_Monetary=("total_order_value", "sum"),
    )
    .sort_values("Total_Monetary", ascending=False)
    .reset_index()
)

st.dataframe(
    seg_leader.style.format({
        "Avg_Freq": "{:.2f}",
        "Avg_Monetary": "Rp {:,.0f}",
        "Total_Monetary": "Rp {:,.0f}",
    }),
    use_container_width=True
)

# =====================
# Top Customers (High Monetary)
# =====================
st.markdown("---")
st.subheader("💰 Top Customers (berdasarkan Monetary)")

df_top = (
    df_rfm_seg
    .sort_values("total_order_value", ascending=False)
    .loc[:, ["Customer_id", "Customer_name", "Segment", "order_cnt", "total_order_value", "day_since_last_order"]]
    .head(20)
    .rename(columns={
        "order_cnt": "Frequency",
        "total_order_value": "Total_Transaksi",
        "day_since_last_order": "Recency(Hari)"
    })
)

st.dataframe(
    df_top.style.format({"Total_Transaksi": "Rp {:,.0f}"}),
    use_container_width=True
)

# =====================
# Insight & Rekomendasi by Segment
# =====================
st.markdown("---")
st.subheader("🧭 Insight & Rekomendasi per Segment")

reco_map = {
    "Champion": "Tawarkan program eksklusif, early access, VIP benefit, atau bundling premium.",
    "Loyal Customers": "Perkuat loyalitas: point reward, subscription, upsell paket hemat.",
    "Potential Loyalists": "Dorong repeat order: voucher repeat, free shipping, reminder WhatsApp.",
    "Can't Lose Them": "Reaktivasi agresif: diskon kuat, paket comeback, personal follow-up.",
    "At Risk": "Winback campaign: diskon terbatas, rekomendasi produk relevan.",
    "About to Sleep": "Kirim konten edukasi + promo ringan untuk mengaktifkan kembali.",
    "New Customers": "Welcome flow: edukasi produk, cross-sell aman, freebie kecil.",
    "Promising": "Nurturing: katalog terbaik, testimoni, social proof, promo bundling.",
    "Need Attention": "Riset hambatan: kualitas, harga, atau stok? Tawarkan trial atau sample.",
    "Others": "Analisa manual untuk strategi spesifik.",
}

# Pilihan segment
seg_list = sorted(df_rfm_seg["Segment"].dropna().unique().tolist())
picked = st.selectbox("Pilih Segment", options=seg_list)
st.info(f"🎯 Rekomendasi untuk **{picked}**: {reco_map.get(picked, '—')}")

# Pencarian nama/ID
search_q = st.text_input("🔎 Cari Customer (Nama/ID)", value="").strip().lower()

df_segview = df_rfm_seg[df_rfm_seg["Segment"] == picked].copy()
if search_q:
    df_segview = df_segview[
        df_segview["Customer_id"].astype(str).str.lower().str.contains(search_q)
        | df_segview["Customer_name"].astype(str).str.lower().str.contains(search_q)
    ]

df_segview_out = (
    df_segview.loc[:, ["Customer_id", "Customer_name", "order_cnt", "total_order_value", "day_since_last_order"]]
    .rename(columns={
        "order_cnt": "Frequency",
        "total_order_value": "Total_Transaksi",
        "day_since_last_order": "Recency(Hari)"
    })
)

st.dataframe(
    df_segview_out.style.format({"Total_Transaksi": "Rp {:,.0f}"}),
    use_container_width=True
)

# =====================
# Unduhan
# =====================
st.markdown("---")
st.subheader("⬇️ Unduh Data")

# Full segmented (dengan nama)
df_rfm_seg_out = (
    df_rfm_seg.rename(columns={
        "order_cnt": "Frequency",
        "total_order_value": "Total_Transaksi",
        "day_since_last_order": "Recency"
    })[["Customer_id", "Customer_name", "Recency", "Frequency", "Total_Transaksi", "Avg_Transaction", "Segment"]]
)
df_rfm_seg_out.to_csv("assets/rfm_segmented.csv", index=False)
with open("assets/rfm_segmented.csv", "rb") as f:
    st.download_button("📥 Download RFM Segmented", f, file_name="rfm_segmented.csv", mime="text/csv")

# Top 20 customers (dengan nama)
df_top.to_csv("assets/top20_customers.csv", index=False)
with open("assets/top20_customers.csv", "rb") as f:
    st.download_button("📥 Download Top 20 Customers", f, file_name="top20_customers.csv", mime="text/csv")

# Segment terpilih (dengan nama + filter)
df_segview_out.to_csv("assets/segment_selected.csv", index=False)
with open("assets/segment_selected.csv", "rb") as f:
    st.download_button(f"📥 Download Data Segment '{picked}' (Filtered)", f, file_name=f"segment_{picked.replace(' ','_').lower()}.csv", mime="text/csv")
