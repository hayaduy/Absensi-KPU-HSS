import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Monitoring Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: CLEAN, MODERN & TRUE CENTER
st.markdown("""
    <style>
    /* Dasar & Background */
    .stApp { background-color: #1a0505; color: #ffffff; }
    
    /* Container Utama */
    .block-container { padding-top: 1rem; max-width: 1200px !important; margin: 0 auto; }

    /* Header Jam Responsif */
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { 
        font-size: clamp(50px, 12vw, 95px); 
        font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 25px rgba(249, 115, 22, 0.5); 
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Running Text */
    .running-text-container { width: 100%; overflow: hidden; margin-bottom: 30px; background: rgba(0,0,0,0.2); padding: 12px 0; border-radius: 10px; }
    .running-text { font-size: clamp(13px, 3.5vw, 18px); font-weight: 600; color: #ffffff; white-space: nowrap; animation: scroll-left 30s linear infinite; display: inline-block; }
    .highlight { color: #facc15; font-weight: 800; text-shadow: 0 0 10px rgba(250, 204, 21, 0.4); }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    /* Input Tanggal Center & Elegant */
    div[data-testid="stDateInput"] {
        width: 100% !important;
        max-width: 350px !important;
        margin: 0 auto !important;
        background: rgba(45, 10, 10, 0.9);
        border: 2px solid #f97316;
        border-radius: 15px;
        padding: 8px;
        box-shadow: 0 0 20px rgba(249, 115, 22, 0.2);
    }
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] input { 
        color: #ffffff !important; text-align: center !important;
        background-color: transparent !important; border: none !important;
        font-size: 20px !important; font-weight: bold !important;
    }

    /* CARD LIST RESPONSIF */
    .row-container {
        display: flex; 
        flex-direction: column; 
        background: linear-gradient(90deg, #2d0a0a 0%, #4c0519 100%);
        padding: 20px; border-radius: 20px; margin-bottom: 15px; border: 1px solid #7f1d1d;
    }
    
    @media (min-width: 768px) {
        .row-container { flex-direction: row; align-items: center; justify-content: space-between; padding: 15px 30px; }
        .col-nama { flex: 4; text-align: left; margin-bottom: 0; }
        .col-data-wrap { flex: 6; border-top: none; border-left: 1px solid rgba(127, 29, 29, 0.5); padding-top: 0; padding-left: 20px; }
    }

    .col-nama { width: 100%; text-align: center; margin-bottom: 15px; }
    .name-box { 
        background: rgba(249, 115, 22, 0.08); 
        padding: 10px 20px; border: 1px solid rgba(249, 115, 22, 0.15); 
        border-radius: 12px; display: inline-block; width: 100%; max-width: 380px; 
    }
    .name-box a { color: #fecaca !important; text-decoration: none !important; font-size: 18px; font-weight: 700; }

    .col-data-wrap { 
        width: 100%; display: flex; justify-content: space-around; 
        text-align: center; border-top: 1px solid rgba(127, 29, 29, 0.5); padding-top: 15px;
    }
    .val-v { font-size: clamp(16px, 4.5vw, 19px); font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; margin-bottom: 5px; }
    
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA & HIRARKI
# Menentukan siapa saja pimpinan untuk logika "LAPOR SEKRETARIS"
PIMPINAN = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE"]

MASTER_PNS = [
    "Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", 
    "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", 
    "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", 
    "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", 
    "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", 
    "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."
]
MASTER_PPPK = [
    "Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", 
    "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", 
    "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", 
    "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"
]
MASTER_ALL = MASTER_PNS + MASTER_PPPK

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
ENTRY_ID = "960346359"

# 4. JAM REALTIME & HEADER
header_placeholder = st.empty()
wita_now = datetime.now() + timedelta(hours=8)

# 5. INPUT TANGGAL
col_l, col_m, col_r = st.columns([1, 1.2, 1])
with col_m:
    tgl_pilihan = st.date_input("Tanggal", wita_now.date())

st.markdown("<br>", unsafe_allow_html=True)

# 6. ENGINE PROSES
def fetch_raw(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        return pd.read_csv(StringIO(res.text))
    except: return pd.DataFrame()

def process_log(df, tgl):
    target = tgl.strftime('%d/%m/%Y'); log = {}
    if not df.empty:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[df.columns[0]]).sort_values(by=df.columns[0])
        for _, r in df.iterrows():
            ts = r.iloc[0]
            if ts.strftime('%d/%m/%Y') == target:
                nama = str(r.iloc[1]).strip()
                if nama not in log:
                    log[nama] = {"m": ts.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if ts.hour < 9 else "TERLAMBAT"}
                if ts.hour >= 15: log[nama]["p"] = ts.strftime("%H:%M")
    return log

def render_list(log, master, is_all=False):
    items = []
    for idx, p in enumerate(master):
        nama = p.strip(); d = log.get(nama, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        
        # LOGIKA KETERANGAN
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): 
                d["k"] = "ALPA"
            elif wita_now.hour >= 16:
                # Logika khusus Kasubbag & Sekretaris
                d["k"] = "LAPOR SEKRETARIS" if nama in PIMPINAN else "LAPOR KASUBBAG"
            elif wita_now.hour >= 9:
                d["k"] = "TERLAMBAT"
        
        w = 1 if d["k"] in ["HADIR", "TERLAMBAT"] and d["m"] != "--:--" else 0
        items.append({"n": nama, "d": d, "w": w, "h": idx})

    if is_all: 
        items = sorted(items, key=lambda x: (x['w'], x['h']))

    for it in items:
        n = it["n"]; d = it["d"]; cl = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"] in ["TERLAMBAT", "LAPOR KASUBBAG", "LAPOR SEKRETARIS"] else "#f87171"
        f = FORM_PNS if n in MASTER_PNS else FORM_PPPK
        link = f"{f}?entry.{ENTRY_ID}={n.replace(' ', '+')}&submit=Submit"
        
        st.markdown(f"""
            <div class="row-container">
                <div class="col-nama">
                    <div class="name-box"><a href="{link}" target="_blank">{n.split(',')[0]}</a></div>
                </div>
                <div class="col-data-wrap">
                    <div><div class="label-k">Pagi</div><div class="val-v">{d['m']}</div></div>
                    <div><div class="label-k">Sore</div><div class="val-v">{d['p']}</div></div>
                    <div><div class="label-k">Ket</div><div style="color:{cl}; font-weight:900;">{d['k']}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 7. TAMPILAN TAB
log_pns = process_log(fetch_raw(URL_PNS), tgl_pilihan)
log_pppk = process_log(fetch_raw(URL_PPPK), tgl_pilihan)
log_all = {**log_pns, **log_pppk}

t_a, t_p, t_k = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
with t_a: render_list(log_all, MASTER_ALL, is_all=True)
with t_p: render_list(log_pns, MASTER_PNS)
with t_k: render_list(log_pppk, MASTER_PPPK)

# 8. JAM & AUTO-REFRESH 1 MENIT
while True:
    now = datetime.now() + timedelta(hours=8)
    header_placeholder.markdown(f"""
        <div class="header-jam">
            <div class="clock-text">{now.strftime("%H:%M:%S")}</div>
            <div class="running-text-container">
                <div class="running-text">
                    ABSENSI KPU Kabupaten Hulu Sungai Selatan &nbsp; • &nbsp; 
                    <span class="highlight">Silahkan Cek Kehadiran hari ini yaa, yang belum absen bisa klik di bagian Nama masing-masing</span> &nbsp; • &nbsp; 
                    KPU Kabupaten Hulu Sungai Selatan
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if now.second == 0: st.rerun()
    time.sleep(1)
