import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS TOTAL REPAIR ---
st.markdown("""
    <style>
    /* Meratakan Header ke Tengah */
    .stApp h1, .stApp h2, .stApp h3 { text-align: center !important; }
    
    /* Tombol Cek Absen di Tengah */
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 220px !important;
        height: 50px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Memperbesar Tab Jenis Pegawai */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: bold !important; }

    /* CSS Tabel: Anti-Melorot & Scroll ke Samping */
    .table-container {
        width: 100%;
        overflow-x: auto; /* Aktifkan scroll kanan-kiri di HP */
        margin-top: 20px;
    }
    .absen-table {
        width: 100%;
        min-width: 500px; /* Paksa lebar minimal agar kolom tidak tumpuk */
        border-collapse: collapse;
        font-size: 14px;
    }
    .absen-table th { background-color: #2c3e50; color: white; padding: 12px 8px; text-align: left; }
    .absen-table td { padding: 10px 8px; border-bottom: 1px solid #444; }
    .absen-table tr:nth-child(even) { background-color: rgba(255, 255, 255, 0.05); }
    
    /* Tombol Absen di Bawah */
    .action-btn button {
        width: 100% !important;
        font-size: 12px !important;
        padding: 5px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA MASTER ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

# --- HEADER & JAM ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown("<h3>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<h1 style='text-align: center; color: #3498db; font-size: 55px; margin-top: -15px;'>{wita_now.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

# --- KONTROL TENGAH ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
    if st.button("🔍 CEK ABSEN"):
        st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        for col in df.columns[:2]:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='ignore')
        return df
    except: return pd.DataFrame()

def display_absen(df, master, form_url):
    t_limit = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        df_clean = df.copy()
        time_col, name_col = df_clean.columns[0], df_clean.columns[1]
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], errors='coerce')
        df_clean = df_clean.dropna(subset=[time_col])
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        for _, r in df_day.iterrows():
            nama, jam = str(r[name_col]).strip(), r[time_col].time()
            if nama not in log:
                log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}
            elif jam >= t_pulang:
                log[nama]["p"] = jam.strftime("%H:%M")

    # BANGUN TABEL HTML (PENTING: Gunakan div overflow)
    html_code = f"""
    <div class='table-container'>
        <table class='absen-table'>
            <thead>
                <tr><th>#</th><th>NAMA PEGAWAI</th><th>MASUK</th><th>PULANG</th><th>STATUS</th></tr>
            </thead>
            <tbody>
    """
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "❌"})
        color = "#2ecc71" if "HADIR" in d["k"] else "#e67e22" if "TERLAMBAT" in d["k"] else "#e74c3c"
        st_label = "HDR" if "HADIR" in d["k"] else "TLT" if "TERLAMBAT" in d["k"] else "ALPA"
        
        html_code += f"""
            <tr>
                <td>{i}</td>
                <td><b>{p}</b></td>
                <td>{d['m']}</td>
                <td>{d['p']}</td>
                <td style='color: {color}; font-weight: bold;'>{st_label}</td>
            </tr>
        """
    html_code += "</tbody></table></div>"
    st.markdown(html_code, unsafe_allow_html=True)
    
    # Bagian Tombol Absen di Bawah
    st.markdown("<br><b>KLIK NAMA UNTUK ABSEN:</b>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, p in enumerate(sorted(master)):
        with cols[i % 2]:
            nama_panggil = p.split(',')[0]
            if st.button(f"👉 {nama_panggil}", key=f"btn_{p}_{i}"):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ {p} Sukses!")
                time.sleep(0.5)
                st.rerun()

tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: display_absen(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: display_absen(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
