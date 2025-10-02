import pandas as pd
import numpy as np

# 1) Data Cleaning
def bersihkan_data(df):
    # Bersihkan harga ke numerik
    df['Price_clean'] = (
        df['Price'].astype(str)
        .str.replace('Rp', '', regex=False)
        .str.replace('.', '', regex=False)
        .str.replace(',', '.', regex=False)
        .str.strip()
    )
    df['Price_clean'] = pd.to_numeric(df['Price_clean'], errors='coerce')

    # Normalisasi kolom penting
    df['Order_id'] = df['Order_id'].fillna(method='ffill')
    df['Order_date'] = pd.to_datetime(df['Order_date'], errors='coerce')

    # Drop baris invalid
    df = df.dropna(subset=['Customer_id', 'Order_date', 'Price_clean']).copy()

    # Customer_id jadi string tanpa ".0"
    df['Customer_id'] = df['Customer_id'].astype(float).astype(int).astype(str)

    # Total transaksi
    df['Total_Transaksi'] = df['Quantity'] * df['Price_clean']
    df = df[df['Total_Transaksi'] > 0]

    # Simpan untuk download
    df.to_csv("assets/data_bersih.csv", index=False)
    return df

# 2) Hitung RFM
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
    df_agg['Avg_Transaction'] = (
        (df_agg['Total_Transaksi'] / df_agg['Frequency'])
        .fillna(0).round(0).astype(int)
    )

    # Simpan untuk download
    df_agg.to_csv("assets/rfm_result.csv", index=False)
    return df_agg
