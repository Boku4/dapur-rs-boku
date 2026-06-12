import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

# FUNGSI KONEKSI
def get_db():
    conn = sqlite3.connect('dapur_rumah_sakit.db')
    conn.row_factory = sqlite3.Row
    return conn

st.title("🏥 Sistem Informasi Inventaris Dapur")

# SIDEBAR MENU
menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Bahan"])

# LOGIKA MENU
if menu == "📋 Lihat Stok":
    st.subheader("📦 Monitoring Stok")
    conn = get_db()
    df = pd.read_sql_query('SELECT * FROM mst_items', conn) # Contoh query sederhana
    st.table(df)
    conn.close()

elif menu == "⚙️ Manajemen Bahan":
    st.subheader("⚙️ Manajemen Bahan")
    sub = st.sidebar.radio("Sub-Menu:", ["➕ Tambah Baru", "🗑️ Hapus"])
    conn = get_db()
    if sub == "➕ Tambah Baru":
        with st.form("tambah"):
            nama = st.text_input("Nama Barang:")
            kategori = st.selectbox("Kategori:", ["Bahan Basah", "Bahan Kering"])
            if st.form_submit_button("Simpan"):
                conn.execute('INSERT INTO mst_items (nama_barang, jenis_bahan) VALUES (?, ?)', (nama, kategori))
                conn.commit()
                st.success("Berhasil!")
    conn.close()

else:
    st.write("Silakan pilih menu di samping untuk memulai.")
