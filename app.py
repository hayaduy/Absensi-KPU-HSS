import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Monitoring Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: FULLY RESPONSIVE (MOBILE & DESKTOP)
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
    
    /* Responsive Jam */
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { 
        font-size: clamp(40px, 8vw, 85px); /* Ukuran dinamis sesuai layar */
        font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 20px rgba(249, 115, 22, 0.4); 
        font-family: 'Courier New', Courier, monospace;
    }
    
    /* Running Text */
    .running-text-container { width: 100%; overflow: hidden; margin-bottom: 20px; background: rgba(0,0,0,0.2); padding: 8px 0; }
    .running-text { font-size: 16px; font-weight: 600; color: #ffffff; white-space: nowrap; animation: scroll-left 30s linear infinite; display: inline-block; }
    .highlight { color: #facc15; font-weight: 800; }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    /* Responsif Input Tanggal & Tombol */
    div[data-testid="stDateInput"], .stButton > button {
        width: 100% !important;
        max-width: 400px !important;
        margin: 10px auto !important;
        display: block;
    }
    div[data-testid="stDateInput"] { background: rgba(45, 10, 10, 0.8); border: 2px solid #f97316; border-radius: 15px; padding: 2px; }
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] input { color: #ffffff !important; text-align: center !important; background: transparent !important; border: none !important; font-size: 16px !important; }

    .stButton > button { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; height: 55px !important; font-size: 18px !important; font-weight: 800 !important; 
        border-radius: 15px !important; border: none !important; box-shadow: 0 4px 15px rgba(234, 88, 12, 0.3) !important;
    }

    /* List Baris Pegawai Responsif */
    .row-container {
        display: flex; flex-wrap: wrap; align-items: center; 
        background: linear-gradient(90deg, #2d0a0a 0%, #4c0519 100%);
        padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #7f1d1d;
        max-width: 1100px; margin-left: auto; margin-right: auto;
    }
    
    .col-nama { flex: 1 1 100%; margin-bottom: 10px; text-align: center; }
    @media (min-width: 768px) { .col-nama { flex: 4; margin-bottom: 0; text-align: left; } }

    .name-box { background: rgba(249, 115, 22, 0.08); padding: 8px 15px; border: 1px solid rgba(249, 115, 22, 0.15); border-radius: 10px; display: inline-block; width: 100%; max-width: 300px; }
    .name-box a { color: #fca5a5 !important; text-decoration: none !important; font-size: 16px; font-weight: 600; }

    .col-data-wrap { 
        flex: 1 1 100%; display: flex; justify-content: space-around; 
        text-align: center; border-top: 1px solid #7f1d1d; padding-top: 10px;
    }
    @media (min-width: 768px) { .col-data-wrap { flex: 6; border-top: none; border-left: 1px solid #7f1d1d; padding-top: 0; } }

    .val-v { font-size: 16px; font-weight: 800; color: #ffffff; }
    .label-k { font-size: 9px; color: #fca5a5; text-transform: uppercase; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 5px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 12px !important; padding: 10px 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA (HIRARKI TETAP)
MASTER_PNS = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."]
MASTER_PPPK = ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
MASTER_ALL_HIERARCHY = MASTER_PNS + MASTER_PPPK

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
ENTRY_ID = "960346359"

# 4. JAM REALTIME & HEADER
placeholder_header = st.empty()
wita_now = datetime.now() + timedelta(hours=8)

# 5. TATA LETAK CENTER (RESPONSIF)
# Di Mobile, columns akan otomatis stacking (bertumpuk)
spacer_l, center_col, spacer_r = st.columns([0.2, 1, 0.2])
with center_col:
    tgl_pilihan = st.date_input("Tanggal", wita_now.date())
    if st.button("🔍 SCAN DATA SEKARANG"):
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# 6. FUNGSI LOAD & RENDER
def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        return pd.read_csv(StringIO(res.text))
    except: return pd.DataFrame()

def process_log(df, tgl_pilihan):
    today = tgl_pilihan.strftime('%d/%m/%Y')
    log = {}
    if not df.empty:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[df.columns[0]]).sort_values(by=df.columns[0])
        for _, r in df.iterrows():
            ts = r.iloc[0]
            if ts.strftime('%d/%m/%Y') == today:
                nama = str(r.iloc[1]).strip()
                if nama not in log:
                    log[nama] = {"m": ts.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if ts.hour < 9 else "TERLAMBAT"}
                if ts.hour >= 15: log[nama]["p"] = ts.strftime("%H:%M")
    return log

def render_list(log, master_order, sort_priority=False):
    list_to_show = []
    for idx, p in enumerate(master_order):
        nama_p = p.strip()
        d = log.get(nama_p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
            elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
            elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"
        
        weight = 1 if d["k"] in ["HADIR", "TERLAMBAT"] and d["m"] != "--:--" else 0
        list_to_show.append({"nama": nama_p, "data": d, "w": weight, "h": idx})

    if sort_priority:
        list_to_show = sorted(list_to_show, key=lambda x: (x['w'], x['h']))
    else:
        list_to_show = sorted(list_to_show, key=lambda x: x['h'])

    for i, item in enumerate(list_to_show, 1):
        nama_p = item["nama"]; d = item["data"]
        clr = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        target_form = FORM_PNS if nama_p in MASTER_PNS else FORM_PPPK
        link = f"{target_form}?entry.{ENTRY_ID}={nama_p.replace(' ', '+')}&submit=Submit"
        
        st.markdown(f"""
        <div class="row-container">
            <div class="col-nama">
                <div class="name-box"><a href="{link}" target="_blank">{i}. {nama_p.split(',')[0]}</a></div>
            </div>
            <div class="col-data-wrap">
                <div><div class="label-k">Pagi</div><div class="val-v">{d['m']}</div></div>
                <div><div class="label-k">Sore</div><div class="val-v">{d['p']}</div></div>
                <div><div class="label-k">Ket</div><div style="color:{clr}; font-weight:900;">{d['k']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 7. LOAD & TAB
log_pns = process_log(fetch_data(URL_PNS), tgl_pilihan)
log_pppk = process_log(fetch_data(URL_PPPK), tgl_pilihan)
combined_log = {**log_pns, **log_pppk}

tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
with tab_all: render_list(combined_log, MASTER_ALL_HIERARCHY, True)
with tab_pns: render_list(log_pns, MASTER_PNS)
with tab_pppk: render_list(log_pppk, MASTER_PPPK)

# 8. REALTIME CLOCK & REFRESH
while True:
    tick = datetime.now() + timedelta(hours=8)
    placeholder_header.markdown(f"""
        <div class="header-jam">
            <div class="clock-text">{tick.strftime("%H:%M:%S")}</div>
            <div class="running-text-container">
                <div class="running-text">
                    KPU HSS &nbsp; • &nbsp; <span class="highlight">Cek Kehadiran hari ini, Klik Nama untuk Absen</span> &nbsp; • &nbsp; MONITORING ABSENSI
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if tick.second == 0: st.rerun()
    time.sleep(1)
