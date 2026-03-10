import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Monitoring Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: STICKY HEADER & CLEAN LAYOUT
st.markdown("""
    <style>
    /* Dasar & Background */
    .stApp { background-color: #1a0505; color: #ffffff; }
    
    /* Container Utama */
    .block-container { padding-top: 0rem; max-width: 1200px !important; margin: 0 auto; }

    /* --- STICKY HEADER SECTION --- */
    .sticky-wrapper {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: #1a0505;
        z-index: 999;
        padding-top: 10px;
        padding-bottom: 10px;
        border-bottom: 2px solid #7f1d1d;
    }

    .header-jam { text-align: center; }
    .clock-text { 
        font-size: clamp(40px, 10vw, 85px); 
        font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 20px rgba(249, 115, 22, 0.5); 
        font-family: 'Courier New', Courier, monospace;
        margin: 0;
    }
    
    .running-text-container { 
        width: 100%; overflow: hidden; margin: 10px 0; 
        background: rgba(0,0,0,0.3); padding: 8px 0; border-radius: 8px; 
    }
    .running-text { font-size: clamp(12px, 3vw, 16px); font-weight: 600; color: #ffffff; white-space: nowrap; animation: scroll-left 30s linear infinite; display: inline-block; }
    .highlight { color: #facc15; font-weight: 800; }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    /* Input Tanggal agar tetap proporsional di Sticky Header */
    div[data-testid="stDateInput"] {
        width: 100% !important;
        max-width: 300px !important;
        margin: 5px auto !important;
        background: rgba(45, 10, 10, 0.9);
        border: 2px solid #f97316;
        border-radius: 12px;
        padding: 5px;
    }
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] input { 
        color: #ffffff !important; text-align: center !important;
        background-color: transparent !important; border: none !important;
        font-size: 18px !important; font-weight: bold !important;
    }

    /* --- CONTENT SECTION --- */
    .row-container {
        display: flex; flex-direction: column; 
        background: linear-gradient(90deg, #2d0a0a 0%, #4c0519 100%);
        padding: 15px; border-radius: 15px; margin-bottom: 12px; border: 1px solid #7f1d1d;
    }
    
    @media (min-width: 768px) {
        .row-container { flex-direction: row; align-items: center; justify-content: space-between; padding: 12px 25px; }
        .col-nama { flex: 4; text-align: left; margin-bottom: 0; }
        .col-data-wrap { flex: 6; border-top: none; border-left: 1px solid rgba(127, 29, 29, 0.5); padding-top: 0; padding-left: 20px; }
    }

    .col-nama { width: 100%; text-align: center; margin-bottom: 10px; }
    .name-box { 
        background: rgba(249, 115, 22, 0.08); padding: 8px 15px; 
        border: 1px solid rgba(249, 115, 22, 0.15); border-radius: 10px; 
        display: inline-block; width: 100%; max-width: 350px; 
    }
    .name-box a { color: #fecaca !important; text-decoration: none !important; font-size: 16px; font-weight: 700; }

    .col-data-wrap { 
        width: 100%; display: flex; justify-content: space-around; 
        text-align: center; border-top: 1px solid rgba(127, 29, 29, 0.5); padding-top: 10px;
    }
    .val-v { font-size: clamp(15px, 4vw, 18px); font-weight: 800; color: #ffffff; }
    .label-k { font-size: 9px; color: #fca5a5; text-transform: uppercase; margin-bottom: 3px; }
    
    /* Tabs styling */
    .stTabs { margin-top: 10px; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA
MASTER_PNS = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hiyati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."]
MASTER_PPPK = ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
MASTER_ALL = MASTER_PNS + MASTER_PPPK

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
ENTRY_ID = "960346359"

# 4. JAM & STICKY HEADER AREA
header_placeholder = st.empty()
wita_now = datetime.now() + timedelta(hours=8)

# Menggunakan div sticky-wrapper untuk membungkus Jam dan Tanggal
# Catatan: Di Streamlit, kita perlu menyisipkan CSS sticky ini via markdown secara strategis
with st.container():
    st.markdown('<div class="sticky-wrapper">', unsafe_allow_html=True)
    
    # Placeholder untuk Jam (akan diupdate oleh loop di bawah)
    clock_area = st.empty()
    
    # Input Tanggal (berada di dalam sticky wrapper)
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        tgl_pilihan = st.date_input("Tanggal", wita_now.date(), key="sticky_date")
    
    st.markdown('</div>', unsafe_allow_html=True)

# 5. ENGINE FUNGSI
def fetch_raw(url):
    try: return pd.read_csv(StringIO(requests.get(f"{url}&nc={random.random()}").text))
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
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
            elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
            elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"
        w = 1 if d["k"] in ["HADIR", "TERLAMBAT"] and d["m"] != "--:--" else 0
        items.append({"n": nama, "d": d, "w": w, "h": idx})

    if is_all: items = sorted(items, key=lambda x: (x['w'], x['h']))

    for i, it in enumerate(items, 1):
        n = it["n"]; d = it["d"]; cl = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        f = FORM_PNS if n in MASTER_PNS else FORM_PPPK
        link = f"{f}?entry.{ENTRY_ID}={n.replace(' ', '+')}&submit=Submit"
        st.markdown(f"""
            <div class="row-container">
                <div class="col-nama">
                    <div class="name-box"><a href="{link}" target="_blank">{i}. {n.split(',')[0]}</a></div>
                </div>
                <div class="col-data-wrap">
                    <div><div class="label-k">Pagi</div><div class="val-v">{d['m']}</div></div>
                    <div><div class="label-k">Sore</div><div class="val-v">{d['p']}</div></div>
                    <div><div class="label-k">Ket</div><div style="color:{cl}; font-weight:900;">{d['k']}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 6. TAMPILAN TAB
log_pns = process_log(fetch_raw(URL_PNS), tgl_pilihan)
log_pppk = process_log(fetch_raw(URL_PPPK), tgl_pilihan)
log_all = {**log_pns, **log_pppk}

t_a, t_p, t_k = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
with t_a: render_list(log_all, MASTER_ALL, is_all=True)
with t_p: render_list(log_pns, MASTER_PNS)
with t_k: render_list(log_pppk, MASTER_PPPK)

# 7. UPDATE CLOCK REALTIME
while True:
    now = datetime.now() + timedelta(hours=8)
    clock_area.markdown(f"""
        <div class="header-jam">
            <div class="clock-text">{now.strftime("%H:%M:%S")}</div>
            <div class="running-text-container">
                <div class="running-text">
                    KPU HSS &nbsp; • &nbsp; <span class="highlight">Silahkan Cek Kehadiran hari ini yaa, Klik Nama masing-masing untuk Absen</span> &nbsp; • &nbsp; KPU HSS
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if now.second == 0: st.rerun()
    time.sleep(1)
