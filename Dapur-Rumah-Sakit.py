import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

st.set_page_config(page_title="Inventaris Dapur RS", layout="wide")

# --- DATA AKUN LOGIN (BISA ANDA UBAH DI SINI) ---
USER_CREDENTIALS = {
    "admin_dapur": "DapurRSKeamanan2026",
    "staf_gizi": "LogistikDapurMaju"
}

# --- FUNGSI HALAMAN LOGIN ---
def halaman_login():
    st.markdown('<style>.stApp { background-color: #f4f9f4 !important; }</style>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #1a3a2a;'>🔒 Gerbang Keamanan Sistem</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Silakan masuk menggunakan akun resmi Instalasi Gizi Rumah Sakit</p>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            username = st.text_input("Username / Nama Pengguna:")
            password = st.text_input("Password / Kata Sandi:", type="password")
            tombol_masuk = st.form_submit_button("🔓 MASUK KE SISTEM")
            
            if tombol_masuk:
                if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                    st.session_state["terautentikasi"] = True
                    st.session_state["user_aktif"] = username
                    st.rerun()
                else:
                    st.error("❌ Username atau Password salah! Silakan periksa kembali.")

# --- INISIALISASI STATUS LOGIN ---
if "terautentikasi" not in st.session_state:
    st.session_state["terautentikasi"] = False

# --- JIKA BELUM LOGIN, PAKSA TAMPILKAN HALAMAN LOGIN ---
if not st.session_state["terautentikasi"]:
    halaman_login()
else:
    # ====================================================
    # JIKA SUDAH LOGIN, TAMPILKAN APLIKASI UTAMA DI BAWAH INI
    # ====================================================
    
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

    # Header Atas & Tombol Logout
    col_judul, col_logout = st.columns([4, 1])
    with col_judul:
        st.title("🏥 Sistem Informasi Inventaris Dapur Rumah Sakit")
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Keluar / Logout"):
            st.session_state["terautentikasi"] = False
            st.session_state["user_aktif"] = None
            st.rerun()
            
    st.markdown(f"**Pengguna Aktif:** `{st.session_state['user_aktif']}`")
    st.markdown("---")

    menu = st.sidebar.radio("✨ PILIH TINDAKAN:", ["📋 Lihat Dasbor Stok Gudang", "➕ Input Barang Masuk", "➖ Input Barang Keluar", "⚙️ Manajemen Data Master"])
    
    conn = get_db_connection()
    list_staf = [row['nama_staf'] for row in conn.execute('SELECT nama_staf FROM mst_staff').fetchall()]
    list_barang = {row['nama_barang']: row['item_id'] for row in conn.execute('SELECT nama_barang, item_id FROM mst_items').fetchall()}

    # Query Data Stok
    query = '''
    SELECT b.batch_id AS [ID Batch], i.nama_barang AS [Nama Bahan Makanan], i.jenis_bahan AS [Kategori], 
           b.sisa_stok AS [Sisa Stok], i.satuan AS [Satuan], b.expired_date AS [Tanggal Kadaluarsa],
           CAST(julianday(b.expired_date) - julianday('now') AS INTEGER) AS [Sisa Hari]
    FROM trx_inventory_batches b
    JOIN mst_items i ON b.item_id = i.item_id
    WHERE b.sisa_stok > 0 ORDER BY b.expired_date ASC;
    '''
    df_stok = pd.read_sql_query(query, conn)

    if menu == "📋 Lihat Dasbor Stok Gudang":
        st.subheader("📦 Monitoring Sisa Stok Real-Time (Prioritas FEFO)")
        if df_stok.empty:
            st.info("Stok kosong.")
        else:
            def highlight_fefo(row):
                hari = row['Sisa Hari']
                if hari <= 7: return ['background-color: #ffcdd2'] * len(row)
                elif hari <= 30: return ['background-color: #fff9c4'] * len(row)
                return [''] * len(row)
                
            st.dataframe(df_stok.style.apply(highlight_fefo, axis=1), use_container_width=True, hide_index=True)
            
            # --- PROSES KONVERSI KE EXCEL ---
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_stok.to_excel(writer, sheet_name='Sisa Stok Dapur', index=False)
            data_excel = buffer.getvalue()
            
            st.markdown("<br>", unsafe_allow_html=True)
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
        elif menu == "⚙️ Manajemen Data Master":
     st.subheader("🛠 Edit & Hapus Bahan")
     # Menampilkan tabel barang
     barang_list = conn.execute('SELECT * FROM mst_items').fetchall()
     df_barang = pd.DataFrame(barang_list, columns=['ID', 'Nama Bahan', 'Kategori', 'Satuan'])
     st.table(df_barang)

     # Form Hapus
     id_hapus = st.number_input("Masukkan ID Barang yang ingin dihapus:", min_value=1, step=1)
     if st.button("🗑️ Hapus Barang"):
         # Cek apakah barang dipakai di transaksi
         cek_transaksi = conn.execute('SELECT * FROM trx_inventory_batches WHERE item_id = ?', (id_hapus,)).fetchone()
         if cek_transaksi:
             st.error("Barang ini tidak bisa dihapus karena sudah ada riwayat transaksinya!")
         else:
             conn.execute('DELETE FROM mst_items WHERE item_id = ?', (id_hapus,))
             conn.commit()
             st.success("Data berhasil dihapus!")
             st.rerun()
        st.subheader("Form Pengambilan Bahan Harian")
        if df_stok.empty:
            st.error("Tidak ada stok.")
        else:
            with st.form("form_keluar", clear_on_submit=True):
                pilihan_batch = [f"Batch #{row['ID Batch']} - {row['Nama Bahan Makanan']} (Sisa: {row['Sisa Stok']})" for idx, row in df_stok.iterrows()]
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
