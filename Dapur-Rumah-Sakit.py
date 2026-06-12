import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

# --- DATA AKUN LOGIN ---
USER_CREDENTIALS = {"admin_dapur": "DapurRSKeamanan2026", "staf_gizi": "LogistikDapurMaju"}

# --- FUNGSI HALAMAN LOGIN ---
def halaman_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='text-align: center;'>🔒 Gerbang Keamanan</h2>", unsafe_allow_html=True)
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

    st.title("🏥 Sistem Informasi Inventaris Dapur")
    if st.button("🚪 Logout"):
        st.session_state["terautentikasi"] = False
        st.rerun()
        
    menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Dasbor Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Data Master"])
    conn = get_db_connection()
    
    # Ambil data pembantu
    try:
        list_staf = [row['nama_staf'] for row in conn.execute('SELECT nama_staf FROM mst_staff').fetchall()]
        list_barang = {row['nama_barang']: row['item_id'] for row in conn.execute('SELECT nama_barang, item_id FROM mst_items').fetchall()}
    except:
        st.error("Database belum siap. Pastikan file .db sudah benar.")

    if menu == "📋 Lihat Dasbor Stok":
        st.subheader("📦 Monitoring Stok")
        query = '''SELECT b.batch_id AS [ID Batch], i.nama_barang AS [Nama Bahan], b.sisa_stok AS [Sisa], i.satuan AS [Satuan], b.expired_date AS [Kadaluarsa]
                   FROM trx_inventory_batches b JOIN mst_items i ON b.item_id = i.item_id WHERE b.sisa_stok > 0'''
        st.dataframe(pd.read_sql_query(query, conn), use_container_width=True)

    elif menu == "➕ Input Barang Masuk":
        with st.form("masuk"):
            pilih = st.selectbox("Barang:", list(list_barang.keys()))
            jml = st.number_input("Jumlah:", min_value=0.1)
            tgl = st.date_input("Exp Date:")
            if st.form_submit_button("💾 Simpan"):
                conn.execute('INSERT INTO trx_inventory_batches (item_id, sisa_stok, expired_date) VALUES (?, ?, ?)', (list_barang[pilih], jml, str(tgl)))
                conn.commit()
                st.success("Berhasil!")

    elif menu == "➖ Input Barang Keluar":
        df_stok = pd.read_sql_query('SELECT * FROM trx_inventory_batches b JOIN mst_items i ON b.item_id = i.item_id WHERE sisa_stok > 0', conn)
        if df_stok.empty: st.warning("Stok kosong")
        else:
            with st.form("keluar"):
                batch_id = st.selectbox("Pilih Batch:", df_stok['batch_id'].tolist())
                jml_keluar = st.number_input("Jumlah Keluar:", min_value=0.1)
                if st.form_submit_button("✅ Konfirmasi"):
                    conn.execute('UPDATE trx_inventory_batches SET sisa_stok = sisa_stok - ? WHERE batch_id = ?', (jml_keluar, batch_id))
                    conn.commit()
                    st.success("Stok diperbarui!")

    elif menu == "⚙️ Manajemen Data Master":
        st.subheader("🛠 Edit & Hapus Bahan")
        st.table(pd.read_sql_query('SELECT * FROM mst_items', conn))
        id_hapus = st.number_input("ID Barang yang dihapus:", min_value=1)
        if st.button("🗑️ Hapus"):
            conn.execute('DELETE FROM mst_items WHERE item_id = ?', (id_hapus,))
            conn.commit()
            st.rerun()

    conn.close()
