import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: FULL FREEZE & ANTI-BLANK (STABIL)
st.markdown("""
    <style>
    /* Dasar & Background */
    .stApp { background-color: #1a0505; color: #ffffff; }
    
    /* Hilangkan Header Bawaan Streamlit */
    header[data-testid="stHeader"] { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* --- BAGIAN YANG DI-FREEZE (JAM, TANGGAL, TAB) --- */
    .top-fixed {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: #1a0505;
        z-index: 1000;
        padding: 10px 0 0 0;
        border-bottom: 3px solid #7f1d1d;
        text-align: center;
    }

    .clock-text { 
        font-size: clamp(40px, 10vw, 80px); 
        font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 20px rgba(249, 115, 22, 0.5); 
        font-family: 'Courier New', Courier, monospace;
        margin: 0;
    }
    
    .running-text-container { 
        width: 100%; overflow: hidden; margin: 10px 0; 
        background: rgba(249, 115, 22, 0.1); padding: 8px 0;
    }
    .running-text { font-size: 15px; font-weight: 600; color: #ffffff; white-space: nowrap; animation: scroll-left 30s linear infinite; display: inline-block; }
    .highlight { color: #facc15; font-weight: 800; }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    /* Input Tanggal Center */
    div[data-testid="stDateInput"] {
        width: 100% !important; max-width: 300px !important; margin: 5px auto !important;
        background: #2d0a0a; border: 2px solid #f97316; border-radius: 12px;
    }
    div[data-testid="stDateInput"] input { color: #ffffff !important; text-align: center !important; font-size: 18px !important; }

    /* Tab Menu Style */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; background-color: #1a0505 !important; }

    /* --- AREA SCROLL (DAFTAR PEGAWAI) --- */
    .scroll-content {
        margin-top: 360px; /* Jarak aman agar tidak tertutup header */
        padding: 20px;
    }
    @media (max-width: 768px) { .scroll-content { margin-top: 300px; } }

    /* Card Baris Pegawai */
    .row-container {
        display: flex; flex-direction: column; 
        background: linear-gradient(90deg, #2d0a0a 0%, #4c0519 100%);
        padding: 15px; border-radius: 15px; margin-bottom: 12px; border: 1px solid #7f1d1d;
        max-width: 1100px; margin: 0 auto 12px auto;
    }
    @media (min-width: 768px) {
        .row-container { flex-direction: row; align-items: center; justify-content: space-between; padding: 12px 25px; }
        .col-nama { flex: 4; text-align: left; }
        .col-data-wrap { flex: 6; border-left: 1px solid rgba(127, 29, 29, 0.5); padding-left: 20px; }
    }
    .name-box { 
        background: rgba(249, 115, 22, 0.1); padding: 8px 15px; 
        border: 1px solid rgba(249, 115, 22, 0.2); border-radius: 10px; 
        display: inline-block; width: 100%; max-width: 350px; text-align: center;
    }
    .name-box a { color: #fecaca !important; text-decoration: none !important; font-size: 17px; font-weight: 700; }
    .col-data-wrap { display: flex; justify-content: space-around; width: 100%; text-align: center; }
    .val-v { font-size: 18px; font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA
MASTER_PNS = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."]
MASTER_PPPK = ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
MASTER_ALL = MASTER_PNS + MASTER_PPPK

# 4. DATA ENGINE
def get_data(url):
    try:
        r = requests.get(f"{url}&nc={random.random()}", timeout=10).text
        df = pd.read_csv(StringIO(r))
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        return df.dropna(subset=[df.columns[0]])
    except: return pd.DataFrame()

wita_now = datetime.now() + timedelta(hours=8)

# 5. FIXED HEADER (JAM, RUNNING TEXT, TANGGAL)
# Menggunakan satu div top-fixed untuk membungkus semuanya
st.markdown('<div class="top-fixed">', unsafe_allow_html=True)
jam_placeholder = st.empty()
st.markdown(f"""
    <div class="running-text-container">
        <div class="running-text">
            ABSENSI KPU HSS &nbsp; • &nbsp; <span class="highlight">Silahkan Cek Kehadiran hari ini yaa, yang belum absen bisa klik di bagian Nama masing-masing</span> &nbsp; • &nbsp; ABSENSI KPU HSS
        </div>
    </div>
""", unsafe_allow_html=True)
tgl_pilihan = st.date_input("Pilih Tanggal", wita_now.date(), label_visibility="collapsed")
tab1, tab2, tab3 = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
st.markdown('</div>', unsafe_allow_html=True)

# 6. RENDER LOGIC
def process_log(df, tgl):
    log = {}
    if not df.empty:
        df_today = df[df.iloc[:, 0].dt.normalize() == pd.Timestamp(tgl)]
        for _, r in df_today.sort_values(by=df.columns[0]).iterrows():
            ts = r.iloc[0]; nama = str(r.iloc[1]).strip().replace("  ", " ")
            if nama not in log:
                log[nama] = {"m": ts.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if ts.hour < 9 else "TERLAMBAT"}
            if ts.hour >= 15: log[nama]["p"] = ts.strftime("%H:%M")
    return log

def display_list(log, master, is_all=False):
    st.markdown('<div class="scroll-content">', unsafe_allow_html=True)
    items = []
    for idx, n in enumerate(master):
        nama = n.strip().replace("  ", " "); d = log.get(nama, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
            elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
            elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"
