import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

# --- DATA AKUN LOGIN ---
USER_CREDENTIALS = {"admin_dapur": "DapurRSKeamanan2026", "staf_gizi": "LogistikDapurMaju"}

if "terautentikasi" not in st.session_state: st.session_state["terautentikasi"] = False

if not st.session_state["terautentikasi"]:
    # (Logika login tetap sama seperti sebelumnya)
    # ... [Kode login dibiarkan sama untuk efisiensi]
    pass 
else:
    conn = sqlite3.connect('dapur_rumah_sakit.db')
    conn.row_factory = sqlite3.Row
    
    st.title("🏥 Sistem Informasi Inventaris Dapur")
    menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Data Master"])

    if menu == "⚙️ Manajemen Data Master":
        st.subheader("🛠 Manajemen Bahan Makanan")
        
        # TAB UNTUK TAMBAH BARANG
        tab1, tab2 = st.tabs(["➕ Tambah Bahan Baru", "🗑️ Lihat & Hapus Bahan"])
        
        with tab1:
            with st.form("tambah_barang"):
                nama_baru = st.text_input("Nama Bahan Baru:")
                kategori = st.selectbox("Kategori:", ["Bahan Basah", "Bahan Kering", "Bumbu", "Lainnya"])
                satuan = st.selectbox("Satuan:", ["kg", "gram", "liter", "pcs", "ikat"])
                if st.form_submit_button("💾 Simpan Bahan Baru"):
                    conn.execute('INSERT INTO mst_items (nama_barang, jenis_bahan, satuan) VALUES (?, ?, ?)', 
                                 (nama_baru, kategori, satuan))
                    conn.commit()
                    st.success(f"Bahan '{nama_baru}' berhasil ditambahkan!")
                    st.rerun()

        with tab2:
            df_barang = pd.read_sql_query('SELECT * FROM mst_items', conn)
            st.table(df_barang)
            id_hapus = st.number_input("Masukkan ID untuk dihapus:", min_value=1, step=1)
            if st.button("🗑️ Hapus Bahan"):
                conn.execute('DELETE FROM mst_items WHERE item_id = ?', (id_hapus,))
                conn.commit()
                st.success("Bahan berhasil dihapus!")
                st.rerun()

    # (Logika menu lain seperti Lihat Stok, Masuk, Keluar tetap sama...)
    conn.close()
