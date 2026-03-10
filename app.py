import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Monitoring Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: RUNNING TEXT, SOFT NAME BOX, & CENTER LAYOUT
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
    
    /* Center Jam */
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { 
        font-size: 85px; font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 30px rgba(249, 115, 22, 0.4); 
        font-family: 'Courier New', Courier, monospace;
        margin-bottom: 5px;
    }
    
    /* Running Text Style */
    .running-text-container {
        width: 100%; overflow: hidden; margin-bottom: 20px;
    }
    .running-text {
        font-size: 18px; font-weight: 600; color: #f97316;
        white-space: nowrap;
        animation: scroll-left 25s linear infinite;
        display: inline-block;
        letter-spacing: 2px;
    }
    @keyframes scroll-left {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    /* Center Date Input */
    div[data-testid="stDateInput"] {
        width: 400px !important;
        margin: 0 auto !important;
        background: rgba(45, 10, 10, 0.8);
        border: 2px solid #f97316;
        border-radius: 15px;
        padding: 5px;
    }
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] input { 
        color: #ffffff !important; text-align: center !important;
        background-color: transparent !important; border: none !important;
        font-size: 18px !important;
    }

    /* Styling Button Scan (Center) */
    .stButton { display: flex; justify-content: center; }
    .stButton > button { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; 
        width: 400px !important; 
        height: 60px !important; font-size: 20px !important; font-weight: 800 !important; 
        border-radius: 15px !important; border: none !important;
        box-shadow: 0 4px 15px rgba(234, 88, 12, 0.3) !important;
    }

    /* List Baris Pegawai */
    .row-container {
        display: flex; align-items: center;
        background: linear-gradient(90deg, #2d0a0a 0%, #4c0519 100%);
        padding: 15px 25px; border-radius: 15px; margin-bottom: 12px; border: 1px solid #7f1d1d;
        max-width: 1100px; margin-left: auto; margin-right: auto;
    }
    
    /* Styling Nama: Sangat Soft & Elegant */
    .col-nama { flex: 4; }
    .name-box {
        background: rgba(249, 115, 22, 0.08); /* Tipis banget bang */
        padding: 8px 18px;
        border: 1px solid rgba(249, 115, 22, 0.15);
        border-radius: 10px;
        display: inline-block;
        min-width: 280px;
    }
    .name-box a { 
        color: #fca5a5 !important; /* Warna merah muda pudar */
        text-decoration: none !important; 
        font-size: 17px; font-weight: 600; 
    }
    .name-box:hover { background: rgba(249, 115, 22, 0.15); border-color: #f97316; transition: 0.3s; }

    .col-data-wrap { 
        flex: 6; display: flex; justify-content: space-around; 
        text-align: center; border-left: 1px solid #7f1d1d; padding: 0 20px;
    }
    .val-v { font-size: 17px; font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; }

    /* Center Tabs */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 10px; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA & SUMBER DATA
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hiyati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
ENTRY_ID = "960346359"

# 4. JAM REALTIME & RUNNING TEXT
placeholder_header = st.empty()
wita_now = datetime.now() + timedelta(hours=8)

# 5. TATA LETAK CENTER (3 KOLOM)
col_l, col_m, col_r = st.columns([1, 1.2, 1])

with col_m:
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

def render_list(df, master, form_url):
    today = tgl_pilihan.strftime('%d/%m/%Y')
    log = {}
    if not df.empty:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[df.columns[0]]).sort_values(by=df.columns[0])
        
        for _, r in df.iterrows():
            ts = r.iloc[0]
            if ts.strftime('%d/%m/%Y') == today:
                nama = str(r.iloc[1]).strip()
                jam_str = ts.strftime("%H:%M")
                if nama not in log:
                    log[nama] = {"m": jam_str, "p": "--:--", "k": "HADIR" if ts.hour < 9 else "TERLAMBAT"}
                if ts.hour >= 15:
                    log[nama]["p"] = jam_str

    for i, p in enumerate(sorted(master), 1):
        nama_p = p.strip()
        d = log.get(nama_p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
            elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
            elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"
            
        clr = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        link_absensi = f"{form_url}?entry.{ENTRY_ID}={nama_p.replace(' ', '+')}&submit=Submit"
        
        st.markdown(f"""
        <div class="row-container">
            <div class="col-nama">
                <div class="name-box">
                    <a href="{link_absensi}" target="_blank">{i}. {nama_p.split(',')[0]}</a>
                </div>
            </div>
            <div class="col-data-wrap">
                <div class="item-box"><div class="label-k">Pagi</div><div class="val-v">{d['m']}</div></div>
                <div class="item-box"><div class="label-k">Sore</div><div class="val-v">{d['p']}</div></div>
                <div class="item-box"><div class="label-k">Ket</div><div style="color:{clr}; font-weight:900;">{d['k']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 7. TABS
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1:
    render_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2:
    render_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)

# 8. LOGIKA JAM REALTIME & AUTO UPDATE HIDDEN (1 MENIT)
while True:
    wita_tick = datetime.now() + timedelta(hours=8)
    placeholder_header.markdown(f"""
        <div class="header-jam">
            <div class="clock-text">{wita_tick.strftime("%H:%M:%S")}</div>
            <div class="running-text-container">
                <div class="running-text">ABSENSI KPU Kabupaten Hulu Sungai Selatan &nbsp; • &nbsp; ABSENSI KPU Kabupaten Hulu Sungai Selatan &nbsp; • &nbsp; ABSENSI KPU Kabupaten Hulu Sungai Selatan</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Auto Update otomatis setiap menit ke-0 (1 menit sekali)
    if wita_tick.second == 0:
        st.rerun()
        
    time.sleep(1)
