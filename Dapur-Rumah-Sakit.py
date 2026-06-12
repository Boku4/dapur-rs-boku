
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

def get_db_connection():
    conn = sqlite3.connect('dapur_rumah_sakit.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- CSS STYLING ---
st.markdown('''
<style>
.stApp {
    background-color: #ffffff !important;
    background-image: linear-gradient(90deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.85) 50%, rgba(215,245,220,0.7) 100%) !important;
    background-attachment: fixed !important;
}
h1 { color: #1a3a2a !important; font-weight: 800 !important; }
.stForm, div[data-testid="stDataFrame"] {
    background-color: rgba(255, 255, 255, 0.9) !important;
    padding: 20px !important;
    border-radius: 15px !important;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05) !important;
    border: 1px solid #d0e0d0 !important;
}
</style>
''', unsafe_allow_html=True)

st.title("🏥 Sistem Informasi Inventaris Dapur Rumah Sakit")
st.markdown("---")

menu = st.sidebar.radio("✨ PILIH MENU:", ["📋 Dasbor Sisa Stok", "➕ Input Barang Masuk", "➖ Input Barang Keluar"])

conn = get_db_connection()
list_staf = [row['nama_staf'] for row in conn.execute('SELECT nama_staf FROM mst_staff').fetchall()]
list_barang = {row['nama_barang']: row['item_id'] for row in conn.execute('SELECT nama_barang, item_id FROM mst_items').fetchall()}

# Query Data Stok
query = '''
SELECT b.batch_id AS [ID Batch], i.nama_barang AS [Nama Bahan], i.jenis_bahan AS [Kategori], 
       b.sisa_stok AS [Sisa Stok], i.satuan AS [Satuan], b.expired_date AS [Tanggal Kadaluarsa],
       CAST(julianday(b.expired_date) - julianday('now') AS INTEGER) AS [Sisa Hari]
FROM trx_inventory_batches b
JOIN mst_items i ON b.item_id = i.item_id
WHERE b.sisa_stok > 0 ORDER BY b.expired_date ASC;
'''
df_stok = pd.read_sql_query(query, conn)

if menu == "📋 Dasbor Sisa Stok":
    st.subheader("📦 Monitoring Stok Real-Time (FEFO)")
    if df_stok.empty:
        st.info("Stok kosong.")
    else:
        def highlight_fefo(row):
            hari = row['Sisa Hari']
            if hari <= 7: return ['background-color: #ffcdd2'] * len(row)
            elif hari <= 30: return ['background-color: #fff9c4'] * len(row)
            return [''] * len(row)
            
        st.dataframe(df_stok.style.apply(highlight_fefo, axis=1), use_container_width=True, hide_index=True)
        
        # --- PROSES KONVERSI KE EXCEL SIAP PAKAI ---
        # Membuat buffer memori agar file Excel bisa diunduh instan
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Data dipindahkan ke lembar kerja Excel bernama 'Sisa Stok Dapur'
            df_stok.to_excel(writer, sheet_name='Sisa Stok Dapur', index=False)
        
        data_excel = buffer.getvalue()
        
        st.markdown("<br>", unsafe_allow_html=True)
        # Tombol Download Excel Resmi
        st.download_button(
            label="📥 Download Laporan Excel Resmi (Siap Print)",
            data=data_excel,
            file_name=f"Laporan_Stok_Dapur_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

elif menu == "➕ Input Barang Masuk":
    st.subheader("Form Barang Masuk")
    with st.form("form_masuk", clear_on_submit=True):
        col1, col2 = st.columns(2)
        pilih_barang = col1.selectbox("Nama Bahan:", list(list_barang.keys()))
        jumlah = col1.number_input("Jumlah:", min_value=0.1)
        tgl_exp = col2.date_input("Tanggal Kadaluarsa:")
        pilih_staf = col2.selectbox("Diterima Oleh:", list_staf)
        if st.form_submit_button("💾 SIMPAN DATA"):
            item_id = list_barang[pilih_barang]
            staf_id = conn.execute('SELECT staff_id FROM mst_staff WHERE nama_staf = ?', (pilih_staf,)).fetchone()['staff_id']
            conn.execute('INSERT INTO trx_inventory_batches (item_id, jumlah_masuk, sisa_stok, tgl_masuk, expired_date, staff_input_id) VALUES (?, ?, ?, ?, ?, ?)', (item_id, jumlah, jumlah, datetime.now().strftime("%Y-%m-%d"), str(tgl_exp), staf_id))
            conn.commit()
            st.success("✅ Berhasil disimpan!")

elif menu == "➖ Input Barang Keluar":
    st.subheader("Form Pengambilan Bahan Harian")
    if df_stok.empty:
        st.error("Tidak ada stok.")
    else:
        with st.form("form_keluar", clear_on_submit=True):
            pilihan_batch = [f"Batch #{row['ID Batch']} - {row['Nama Bahan']} (Sisa: {row['Sisa Stok']})" for idx, row in df_stok.iterrows()]
            pilih_batch_str = st.selectbox("Pilih Barang (Prioritas FEFO Teratas):", pilihan_batch)
            batch_id_terpilih = int(pilih_batch_str.split(" ")[1].replace("#", ""))
            jumlah_keluar = st.number_input("Jumlah Keluar:", min_value=0.1)
            pilih_staf_ambil = st.selectbox("Diambil Oleh:", list_staf)
            keterangan = st.text_input("Keterangan:")
            if st.form_submit_button("✅ KONFIRMASI KELUAR"):
                staf_id = conn.execute('SELECT staff_id FROM mst_staff WHERE nama_staf = ?', (pilih_staf_ambil,)).fetchone()['staff_id']
                data_batch = conn.execute('SELECT sisa_stok FROM trx_inventory_batches WHERE batch_id = ?', (batch_id_terpilih,)).fetchone()
                if data_batch['sisa_stok'] < jumlah_keluar:
                    st.error("Stok tidak cukup!")
                else:
                    conn.execute('UPDATE trx_inventory_batches SET sisa_stok = sisa_stok - ? WHERE batch_id = ?', (jumlah_keluar, batch_id_terpilih))
                    conn.execute('INSERT INTO trx_inventory_out (batch_id, jumlah_keluar, tgl_keluar, staff_ambil_id, keterangan) VALUES (?, ?, ?, ?, ?)', (batch_id_terpilih, jumlah_keluar, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), staf_id, keterangan))
                    conn.commit()
                    st.success("✅ Stok berhasil diperbarui!")
conn.close()
