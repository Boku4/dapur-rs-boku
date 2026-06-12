import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

# FUNGSI KONEKSI DATABASE
def get_db():
    conn = sqlite3.connect('dapur_rumah_sakit.db')
    conn.row_factory = sqlite3.Row
    return conn

st.title("🏥 Sistem Informasi Inventaris Dapur")

# SIDEBAR NAVIGATION
menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Bahan"])

# 1. MENU LIHAT STOK
if menu == "📋 Lihat Stok":
    st.subheader("📦 Monitoring Sisa Stok")
    conn = get_db()
    try:
        df = pd.read_sql_query('SELECT * FROM trx_inventory_batches', conn)
        st.dataframe(df, use_container_width=True)
    except:
        st.info("Data masih kosong atau tabel belum tersedia.")
    conn.close()

# 2. MENU INPUT BARANG MASUK
elif menu == "⚙️ Manajemen Bahan":
    st.subheader("⚙️ Manajemen Bahan")
    conn = get_db()
    nama_baru = st.text_input("Nama Bahan Baru:")
    
    if st.button("➕ Tambah Bahan"):
        if nama_baru:
            try:
                # Menggunakan NULL untuk item_id agar database mengisi angka otomatis (AUTOINCREMENT)
                conn.execute('INSERT INTO mst_items (item_id, nama_barang) VALUES (NULL, ?)', (nama_baru,))
                conn.commit()
                st.success(f"Bahan '{nama_baru}' berhasil ditambahkan!")
                st.rerun() # Refresh agar tabel langsung terupdate
            except Exception as e:
                st.error(f"Eror database: {e}")
        else:
            st.warning("Nama bahan tidak boleh kosong!")
    
    st.write("---")
    df_items = pd.read_sql_query('SELECT * FROM mst_items', conn)
    st.table(df_items)
    conn.close()

# 3. MENU INPUT BARANG KELUAR
elif menu == "➖ Input Barang Keluar":
    st.subheader("➖ Input Barang Keluar")
    conn = get_db()
    batch_id = st.number_input("ID Batch:", min_value=1)
    jml_keluar = st.number_input("Jumlah Keluar:", min_value=0.1)
    if st.button("✅ Kurangi Stok"):
        conn.execute('UPDATE trx_inventory_batches SET sisa_stok = sisa_stok - ? WHERE batch_id = ?', (jml_keluar, batch_id))
        conn.commit()
        st.success("Stok berhasil diperbarui!")
    conn.close()

# 4. MENU MANAJEMEN BAHAN
elif menu == "⚙️ Manajemen Bahan":
    st.subheader("⚙️ Manajemen Bahan")
    conn = get_db()
    nama_baru = st.text_input("Nama Bahan Baru:")
    if st.button("➕ Tambah Bahan"):
        conn.execute('INSERT INTO mst_items (nama_barang) VALUES (?)', (nama_baru,))
        conn.commit()
        st.success("Bahan berhasil ditambahkan!")
    
    st.write("---")
    df_items = pd.read_sql_query('SELECT * FROM mst_items', conn)
    st.table(df_items)
    conn.close()
