import streamlit as st
import sqlite3
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

# Fungsi Koneksi Database
def get_db():
    conn = sqlite3.connect('dapur_rumah_sakit.db')
    conn.row_factory = sqlite3.Row
    return conn

# Header
st.title("🏥 Sistem Informasi Inventaris Dapur")

# --- SIDEBAR MENU ---
# Kita pastikan menu ini selalu tampil di bagian paling atas
menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Bahan"])

# --- LOGIKA TAMPILAN ---
if menu == "📋 Lihat Stok":
    st.subheader("📦 Monitoring Stok")
    conn = get_db()
    df = pd.read_sql_query('SELECT * FROM trx_inventory_batches', conn)
    st.dataframe(df)
    conn.close()

elif menu == "➕ Input Barang Masuk":
    st.subheader("➕ Input Barang Masuk")
    st.write("Silakan isi form input barang masuk...")

elif menu == "➖ Input Barang Keluar":
    st.subheader("➖ Input Barang Keluar")
    st.write("Silakan isi form input barang keluar...")

elif menu == "⚙️ Manajemen Bahan":
    st.subheader("⚙️ Manajemen Bahan")
    conn = get_db()
    nama_baru = st.text_input("Nama Bahan Baru:")
    if st.button("➕ Tambah Bahan"):
        try:
            conn.execute('INSERT INTO mst_items (nama_barang) VALUES (?)', (nama_baru,))
            conn.commit()
            st.success("Berhasil!")
            st.rerun()
        except Exception as e:
            st.error(f"Eror: {e}")
    
    df_items = pd.read_sql_query('SELECT * FROM mst_items', conn)
    st.table(df_items)
    conn.close()
