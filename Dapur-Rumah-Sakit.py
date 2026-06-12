import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

# --- LOGIN ---
# (Pastikan bagian login Anda tetap di sini)

# --- FUNGSI DATABASE ---
def get_db():
    conn = sqlite3.connect('dapur_rumah_sakit.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- MENU & NAVIGASI ---
menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Bahan"])

if menu == "⚙️ Manajemen Bahan":
    # Membuat sub-menu di halaman Manajemen
    sub_menu = st.sidebar.radio("Sub-Menu:", ["➕ Tambah Bahan Baru", "🗑️ Lihat & Hapus Bahan"])
    
    if sub_menu == "➕ Tambah Bahan Baru":
        st.subheader("➕ Tambah Bahan Makanan Baru")
        with st.form("tambah_barang"):
            nama_baru = st.text_input("Nama Bahan Baru:")
            kategori = st.selectbox("Kategori:", ["Bahan Basah", "Bahan Kering", "Bumbu", "Lainnya"])
            satuan = st.selectbox("Satuan:", ["kg", "gram", "liter", "pcs", "ikat"])
            if st.form_submit_button("💾 Simpan ke Database"):
                conn = get_db()
                conn.execute('INSERT INTO mst_items (nama_barang, jenis_bahan, satuan) VALUES (?, ?, ?)', (nama_baru, kategori, satuan))
                conn.commit()
                conn.close()
                st.success(f"Bahan '{nama_baru}' berhasil ditambahkan!")
                
    elif sub_menu == "🗑️ Lihat & Hapus Bahan":
        st.subheader("🗑️ Kelola Daftar Bahan")
        conn = get_db()
        df_barang = pd.read_sql_query('SELECT * FROM mst_items', conn)
        st.table(df_barang)
        
        id_hapus = st.number_input("Masukkan ID Bahan untuk dihapus:", min_value=1, step=1)
        if st.button("🗑️ Hapus Bahan Permanen"):
            conn.execute('DELETE FROM mst_items WHERE item_id = ?', (id_hapus,))
            conn.commit()
            conn.close()
            st.success("Data dihapus!")
            st.rerun()

# --- (Logika menu Lihat Stok, Masuk, Keluar tetap di sini) ---
