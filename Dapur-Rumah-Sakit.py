import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

def get_db():
    conn = sqlite3.connect('dapur_rumah_sakit.db')
    conn.row_factory = sqlite3.Row
    return conn

st.title("🏥 Sistem Informasi Inventaris Dapur")

# --- SIDEBAR ---
menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Bahan"])

conn = get_db()

# --- 1. Lihat Stok ---
if menu == "📋 Lihat Stok":
    st.subheader("📦 Monitoring Sisa Stok")
    query = '''SELECT b.batch_id, i.nama_barang, b.sisa_stok, b.expired_date 
               FROM trx_inventory_batches b 
               JOIN mst_items i ON b.item_id = i.item_id'''
    df = pd.read_sql_query(query, conn)
    st.dataframe(df, use_container_width=True)

# --- 2. Input Barang Masuk ---
elif menu == "➕ Input Barang Masuk":
    st.subheader("➕ Input Barang Masuk")
    items = pd.read_sql_query('SELECT * FROM mst_items', conn)
    item_dict = dict(zip(items['nama_barang'], items['item_id']))
    
    with st.form("form_masuk"):
        pilih_barang = st.selectbox("Pilih Barang:", list(item_dict.keys()))
        jml = st.number_input("Jumlah:", min_value=0.1)
        if st.form_submit_button("💾 Simpan"):
            conn.execute('INSERT INTO trx_inventory_batches (item_id, sisa_stok) VALUES (?, ?)', (item_dict[pilih_barang], jml))
            conn.commit()
            st.success("Berhasil!")
            st.rerun()

# --- 3. Input Barang Keluar ---
elif menu == "➖ Input Barang Keluar":
    st.subheader("➖ Input Barang Keluar")
    df_stok = pd.read_sql_query('SELECT b.batch_id, i.nama_barang, b.sisa_stok FROM trx_inventory_batches b JOIN mst_items i ON b.item_id = i.item_id', conn)
    st.dataframe(df_stok)
    
    with st.form("form_keluar"):
        id_batch = st.number_input("Masukkan ID Batch yang akan dikurangi:", min_value=1)
        jml_keluar = st.number_input("Jumlah Keluar:", min_value=0.1)
        if st.form_submit_button("✅ Kurangi Stok"):
            conn.execute('UPDATE trx_inventory_batches SET sisa_stok = sisa_stok - ? WHERE batch_id = ?', (jml_keluar, id_batch))
            conn.commit()
            st.success("Stok diperbarui!")
            st.rerun()

# --- 4. Manajemen Bahan ---
elif menu == "⚙️ Manajemen Bahan":
    st.subheader("⚙️ Tambah & Kelola Bahan")
    
    # Form Tambah Bahan yang Lengkap
    with st.form("form_tambah_lengkap"):
        nama_baru = st.text_input("Nama Bahan Baru:")
        kategori = st.selectbox("Jenis Bahan:", ["Bahan Basah", "Bahan Kering", "Bumbu", "Lainnya"])
        satuan = st.selectbox("Satuan:", ["kg", "gram", "liter", "pcs", "ikat"])
        harga = st.number_input("Harga Satuan:", min_value=0)
        
        if st.form_submit_button("➕ Tambah ke Daftar"):
            if nama_baru:
                try:
                    # Menambahkan data ke semua kolom yang diminta database
                    conn.execute('INSERT INTO mst_items (nama_barang, jenis_bahan, satuan, harga_satuan) VALUES (?, ?, ?, ?)', 
                                 (nama_baru, kategori, satuan, harga))
                    conn.commit()
                    st.success(f"'{nama_baru}' berhasil ditambahkan!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Eror: {e}")
            else:
                st.warning("Nama bahan tidak boleh kosong.")
    
    st.write("---")
    st.subheader("Daftar Bahan Saat Ini:")
    df_items = pd.read_sql_query('SELECT * FROM mst_items', conn)
    st.table(df_items)

conn.close()
