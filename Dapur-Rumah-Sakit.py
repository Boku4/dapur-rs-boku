import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

# --- DATA AKUN LOGIN ---
USER_CREDENTIALS = {"admin_dapur": "DapurRSKeamanan2026", "staf_gizi": "LogistikDapurMaju"}

# --- FUNGSI LOGIN ---
def halaman_login():
    st.markdown('<style>.stApp { background-color: #f4f9f4 !important; }</style>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #1a3a2a;'>🔒 Gerbang Keamanan Sistem</h2>", unsafe_allow_html=True)
        with st.form("form_login"):
            username = st.text_input("Username:")
            password = st.text_input("Password:", type="password")
            if st.form_submit_button("🔓 MASUK"):
                if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                    st.session_state["terautentikasi"] = True
                    st.session_state["user_aktif"] = username
                    st.rerun()
                else: st.error("❌ Username/Password salah!")

if "terautentikasi" not in st.session_state: st.session_state["terautentikasi"] = False

if not st.session_state["terautentikasi"]:
    halaman_login()
else:
    def get_db_connection():
        conn = sqlite3.connect('dapur_rumah_sakit.db')
        conn.row_factory = sqlite3.Row
        return conn

    # --- MENU UTAMA ---
    st.title("🏥 Sistem Informasi Inventaris Dapur")
    if st.button("🚪 Logout"):
        st.session_state["terautentikasi"] = False
        st.rerun()
        
    menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Dasbor Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Data Master"])
    conn = get_db_connection()

    if menu == "📋 Lihat Dasbor Stok":
        st.subheader("📦 Monitoring Sisa Stok")
        query = '''SELECT b.batch_id AS [ID Batch], i.nama_barang AS [Nama Bahan], b.sisa_stok AS [Sisa], i.satuan AS [Satuan], b.expired_date AS [Kadaluarsa]
                   FROM trx_inventory_batches b JOIN mst_items i ON b.item_id = i.item_id WHERE b.sisa_stok > 0 ORDER BY b.expired_date ASC'''
        df = pd.read_sql_query(query, conn)
        st.dataframe(df, use_container_width=True)

    elif menu == "⚙️ Manajemen Data Master":
        st.subheader("🛠 Edit & Hapus Bahan")
        df_barang = pd.read_sql_query('SELECT * FROM mst_items', conn)
        st.table(df_barang)
        id_hapus = st.number_input("Masukkan ID Barang untuk dihapus:", min_value=1, step=1)
        if st.button("🗑️ Hapus Barang"):
            try:
                conn.execute('DELETE FROM mst_items WHERE item_id = ?', (id_hapus,))
                conn.commit()
                st.success("Data berhasil dihapus!")
                st.rerun()
            except Exception as e:
                st.error("Gagal menghapus: Barang mungkin sudah memiliki riwayat transaksi.")

    # (Lanjutkan dengan logika Input Masuk & Keluar yang lama di sini...)
    # Kode untuk Input Barang Masuk & Keluar Anda sama seperti sebelumnya.
    
    conn.close()
