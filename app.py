import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: FULL FREEZE HEADER & STYLING
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    .block-container { padding: 0 !important; max-width: 100% !important; }

    /* STICKY HEADER AREA */
    .top-fixed {
        position: fixed;
        top: 0; left: 0; right: 0;
        background-color: #1a0505;
        z-index: 1000;
        padding-top: 10px;
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
    
    div[data-testid="stDateInput"] {
        width: 100% !important; max-width: 300px !important; margin: 5px auto !important;
        background: #2d0a0a; border: 2px solid #f97316; border-radius: 12px;
    }
    div[data-testid="stDateInput"] input { color: #ffffff !important; text-align: center !important; font-size: 18px !important; }

    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; background-color: #1a0505 !important; }

    /* CONTENT SCROLL AREA */
    .content-wrapper {
        margin-top: 380px; 
        padding: 0 10px 100px 10px;
    }
    @media (max-width: 768px) { .content-wrapper { margin-top: 320px; } }

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

# 4. ENGINE FUNGSI
def fetch_data(url):
    try:
        r = requests.get(f"{url}&nc={random.random()}", timeout=10).text
        df = pd.read_csv(StringIO(r))
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        return df.dropna(subset=[df.columns[0]])
    except: return pd.DataFrame()

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

wita_now = datetime.now() + timedelta(hours=8)

# 5. FIXED HEADER
st.markdown('<div class="top-fixed">', unsafe_allow_html=True)
jam_placeholder = st.empty()
st.markdown(f"""
    <div class="running-text-container">
        <div class="running-text">
            ABSENSI KPU HSS • <span class="highlight">Silahkan Cek Kehadiran hari ini yaa, yang belum absen bisa klik di bagian Nama masing-masing</span> • ABSENSI KPU HSS
        </div>
    </div>
""", unsafe_allow_html=True)
tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
tabs = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
st.markdown('</div>', unsafe_allow_html=True)

# 6. RENDER LOGIC
def render_list(log, master, is_all=False):
    items = []
    for idx, n in enumerate(master):
        nama = n.strip().replace("  ", " "); d = log.get(nama, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
            elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
            elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"
        w = 1 if d["k"] in ["HADIR", "TERLAMBAT"] and d["m"] != "--:--" else 0
        items.append({"n": nama, "d": d, "w": w, "h": idx})
    
    if is_all: items = sorted(items, key=lambda x: (x['w'], x['h']))
    
    for it in items:
        n = it["n"]; d = it["d"]; cl = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        form = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse" if n in MASTER_PNS else "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
        link = f"{form}?entry.960346359={n.replace(' ', '+')}&submit=Submit"
        st.markdown(f"""
            <div class="row-container">
                <div class="col-nama"><div class="name-box"><a href="{link}" target="_blank">{n.split(',')[0]}</a></div></div>
                <div class="col-data-wrap">
                    <div><div class="label-k">Pagi</div><div class="val-v">{d['m']}</div></div>
                    <div><div class="label-k">Sore</div><div class="val-v">{d['p']}</div></div>
                    <div><div class="label-k">Ket</div><div style="color:{cl}; font-weight:900;">{d['k']}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 7. EXECUTION
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

log_pns = process_log(fetch_data(URL_PNS), tgl_pilihan)
log_pppk = process_log(fetch_data(URL_PPPK), tgl_pilihan)
log_all = {**log_pns, **log_pppk}

with tabs[0]: 
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    render_list(log_all, MASTER_ALL, True)
    st.markdown('</div>', unsafe_allow_html=True)
with tabs[1]:
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    render_list(log_pns, MASTER_PNS)
    st.markdown('</div>', unsafe_allow_html=True)
with tabs[2]:
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    render_list(log_pppk, MASTER_PPPK)
    st.markdown('</div>', unsafe_allow_html=True)

# 8. REALTIME LOOP
while True:
    now = datetime.now() + timedelta(hours=8)
    jam_placeholder.markdown(f'<div class="header-jam"><div class="clock-text">{now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)
    if now.second == 0: st.rerun()
    time.sleep(1)
