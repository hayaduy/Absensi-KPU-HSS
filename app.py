import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Monitoring Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: HYBRID RESPONSIVE ENGINE
st.markdown("""
    <style>
    /* Dasar & Background */
    .stApp { background-color: #1a0505; color: #ffffff; }
    
    /* Container Utama agar Desktop tidak melar */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px !important; margin: 0 auto; }

    /* Header Jam Responsif */
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { 
        font-size: clamp(45px, 10vw, 90px); 
        font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 20px rgba(249, 115, 22, 0.4); 
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Running Text */
    .running-text-container { width: 100%; overflow: hidden; margin-bottom: 25px; background: rgba(0,0,0,0.2); padding: 10px 0; border-radius: 10px; }
    .running-text { font-size: clamp(12px, 3vw, 17px); font-weight: 600; color: #ffffff; white-space: nowrap; animation: scroll-left 30s linear infinite; display: inline-block; }
    .highlight { color: #facc15; font-weight: 800; }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    /* Input & Button Center & Responsive Width */
    div[data-testid="stDateInput"], .stButton > button {
        width: 100% !important;
        max-width: 400px !important;
        margin: 10px auto !important;
        display: block;
    }
    .stButton > button { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; height: 60px !important; font-size: 18px !important; font-weight: 800 !important; 
        border-radius: 15px !important; border: none !important; box-shadow: 0 4px 15px rgba(234, 88, 12, 0.3) !important;
    }

    /* CARD LIST RESPONSIF */
    .row-container {
        display: flex; 
        flex-direction: column; /* Default Mobile: Tumpuk ke bawah */
        background: linear-gradient(90deg, #2d0a0a 0%, #4c0519 100%);
        padding: 20px; border-radius: 20px; margin-bottom: 15px; border: 1px solid #7f1d1d;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.3);
    }
    
    /* Desktop Mode (Layar > 768px) */
    @media (min-width: 768px) {
        .row-container { flex-direction: row; align-items: center; justify-content: space-between; padding: 15px 30px; }
        .col-nama { flex: 4; text-align: left; margin-bottom: 0; }
        .col-data-wrap { flex: 6; border-top: none; border-left: 1px solid rgba(127, 29, 29, 0.5); padding-top: 0; padding-left: 20px; }
    }

    /* Styling Nama Box */
    .col-nama { width: 100%; text-align: center; margin-bottom: 15px; }
    .name-box { 
        background: rgba(249, 115, 22, 0.1); 
        padding: 10px 20px; border: 1px solid rgba(249, 115, 22, 0.2); 
        border-radius: 12px; display: inline-block; width: 100%; max-width: 350px; 
    }
    .name-box a { color: #fecaca !important; text-decoration: none !important; font-size: 17px; font-weight: 700; }

    /* Data (Pagi, Sore, Ket) */
    .col-data-wrap { 
        width: 100%; display: flex; justify-content: space-around; 
        text-align: center; border-top: 1px solid rgba(127, 29, 29, 0.5); padding-top: 15px;
    }
    .val-v { font-size: clamp(15px, 4vw, 18px); font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
    
    /* Tabs Center */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: clamp(5px, 2vw, 20px) !important; }
    .stTabs [data-baseweb="tab"] { font-size: clamp(12px, 3vw, 15px) !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATA & SUMBER
MASTER_PNS = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."]
MASTER_PPPK = ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
MASTER_ALL = MASTER_PNS + MASTER_PPPK

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
ENTRY_ID = "960346359"

# 4. JAM REALTIME & HEADER
header_placeholder = st.empty()
wita_now = datetime.now() + timedelta(hours=8)

# 5. UI CONTROLS (CENTERED)
tgl_pilihan = st.date_input("Tanggal", wita_now.date())
if st.button("🔍 SCAN DATA SEKARANG"):
    st.rerun()

# 6. ENGINE
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

def render_hybrid_list(log, master, is_all=False):
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

# 7. EXECUTION
log_pns = process_log(fetch_raw(URL_PNS), tgl_pilihan)
log_pppk = process_log(fetch_raw(URL_PPPK), tgl_pilihan)
log_all = {**log_pns, **log_pppk}

tab_a, tab_p, tab_k = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
with tab_a: render_hybrid_list(log_all, MASTER_ALL, True)
with tab_p: render_hybrid_list(log_pns, MASTER_PNS)
with tab_k: render_hybrid_list(log_pppk, MASTER_PPPK)

# 8. RESPONSIVE REALTIME CLOCK
while True:
    now = datetime.now() + timedelta(hours=8)
    header_placeholder.markdown(f"""
        <div class="header-jam">
            <div class="clock-text">{now.strftime("%H:%M:%S")}</div>
            <div class="running-text-container">
                <div class="running-text">
                    KPU Kabupaten Hulu Sungai Selatan &nbsp; • &nbsp; <span class="highlight">Silahkan Cek Kehadiran hari ini yaa, yang belum absen bisa klik di bagian Nama masing-masing</span> &nbsp; • &nbsp; MONITORING ABSENSI
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if now.second == 0: st.rerun()
    time.sleep(1)
