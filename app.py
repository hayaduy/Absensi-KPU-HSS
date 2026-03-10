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
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { 
        font-size: 85px; font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 30px rgba(249, 115, 22, 0.4); 
        font-family: 'Courier New', Courier, monospace;
        margin-bottom: 5px;
    }
    .running-text-container {
        width: 100%; overflow: hidden; margin-bottom: 25px;
        background: rgba(0,0,0,0.2); padding: 10px 0;
    }
    .running-text {
        font-size: 19px; font-weight: 600; color: #ffffff;
        white-space: nowrap;
        animation: scroll-left 30s linear infinite;
        display: inline-block;
        letter-spacing: 1px;
    }
    .highlight { color: #facc15; font-weight: 800; text-shadow: 0 0 10px rgba(250, 204, 21, 0.5); }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    div[data-testid="stDateInput"] {
        width: 400px !important; margin: 0 auto !important;
        background: rgba(45, 10, 10, 0.8); border: 2px solid #f97316; border-radius: 15px; padding: 5px;
    }
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] input { color: #ffffff !important; text-align: center !important; background-color: transparent !important; border: none !important; font-size: 18px !important; }

    .stButton { display: flex; justify-content: center; }
    .stButton > button { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; width: 400px !important; height: 60px !important; font-size: 20px !important; font-weight: 800 !important; 
        border-radius: 15px !important; border: none !important; box-shadow: 0 4px 15px rgba(234, 88, 12, 0.3) !important;
    }

    .row-container {
        display: flex; align-items: center; background: linear-gradient(90deg, #2d0a0a 0%, #4c0519 100%);
        padding: 15px 25px; border-radius: 15px; margin-bottom: 12px; border: 1px solid #7f1d1d;
        max-width: 1100px; margin-left: auto; margin-right: auto;
    }
    .col-nama { flex: 4; }
    .name-box { background: rgba(249, 115, 22, 0.08); padding: 8px 18px; border: 1px solid rgba(249, 115, 22, 0.15); border-radius: 10px; display: inline-block; min-width: 280px; }
    .name-box a { color: #fca5a5 !important; text-decoration: none !important; font-size: 17px; font-weight: 600; }
    .name-box:hover { background: rgba(249, 115, 22, 0.15); border-color: #f97316; transition: 0.3s; }
    .col-data-wrap { flex: 6; display: flex; justify-content: space-around; text-align: center; border-left: 1px solid #7f1d1d; padding: 0 20px; }
    .val-v { font-size: 17px; font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; }
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 10px; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA DENGAN URUTAN HIRARKI (STRUKTURAL)
# Urutan: Sekretaris -> Kasubbag -> PNS Lain -> PPPK
MASTER_PNS = [
    "Suwanto, SH., MH.",           # Sekretaris
    "Wawan Setiawan, SH",          # Kasubbag
    "Ineke Setiyaningsih, S.Sos",   # Kasubbag
    "Farah Agustina Setiawati, SH", # Kasubbag
    "Rusma Ariati, SE",            # Kasubbag
    "Helmalina", 
    "Ahmad Erwan Rifani, S.HI", 
    "Syaiful Anwar", 
    "Zainal Hilmi Yustan", 
    "Najmi Hidayati", 
    "Jainal Abidin", 
    "Suci Lestari, S.Ikom", 
    "Athaya Insyira Khairani, S.H", 
    "Muhammad Ibnu Fahmi, S.H.", 
    "Alfian Ridhani, S.Kom", 
    "Muhammad Aldi Hudaifi, S.Kom", 
    "Firda Aulia, S.Kom."
]

MASTER_PPPK = [
    "Sya'bani Rona Baika", 
    "Apriadi Rakhman", 
    "M Satria Maipadly", 
    "Basuki Rahmat", 
    "Sulaiman", 
    "Saldoz Yedi", 
    "Mastoni Ridani", 
    "Suriadi", 
    "Ami Aspihani", 
    "Abdurrahman", 
    "Emaliani", 
    "Muhammad Hafiz Rijani, S.KOM", 
    "Saiful Fahmi, S.Pd", 
    "Nadianti"
]

# Gabungan Hirarki untuk Tab Semua
MASTER_ALL_HIERARCHY = MASTER_PNS + MASTER_PPPK

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
ENTRY_ID = "960346359"

# 4. JAM REALTIME & HEADER
placeholder_header = st.empty()
wita_now = datetime.now() + timedelta(hours=8)

# 5. TATA LETAK CENTER
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
                jam_str = ts.strftime("%H:%M")
                if nama not in log:
                    log[nama] = {"m": jam_str, "p": "--:--", "k": "HADIR" if ts.hour < 9 else "TERLAMBAT"}
                if ts.hour >= 15:
                    log[nama]["p"] = jam_str
    return log

def render_list(log, master_order, sort_priority=False):
    list_to_show = []
    # Menggunakan index urutan master sebagai bobot hirarki
    for idx, p in enumerate(master_order):
        nama_p = p.strip()
        d = log.get(nama_p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
            elif wita_now.hour >= 16: d["k"] = "LAPOR KASUBBAG"
            elif wita_now.hour >= 9: d["k"] = "TERLAMBAT"
            
        # Bobot Status: 0 untuk yang belum absen (supaya naik), 1 untuk yang sudah hadir
        status_weight = 1 if d["k"] in ["HADIR", "TERLAMBAT"] and d["m"] != "--:--" else 0
        list_to_show.append({"nama": nama_p, "data": d, "status_weight": status_weight, "hierarchy_idx": idx})

    # Logika Pengurutan
    if sort_priority:
        # Urutkan berdasarkan status_weight dulu (0 naik), baru berdasarkan hirarki aslinya
        list_to_show = sorted(list_to_show, key=lambda x: (x['status_weight'], x['hierarchy_idx']))
    else:
        # Urutkan murni berdasarkan hirarki (Sekretaris -> Kasubbag -> PNS -> PPPK)
        list_to_show = sorted(list_to_show, key=lambda x: x['hierarchy_idx'])

    for i, item in enumerate(list_to_show, 1):
        nama_p = item["nama"]
        d = item["data"]
        clr = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        target_form = FORM_PNS if nama_p in MASTER_PNS else FORM_PPPK
        link_absensi = f"{target_form}?entry.{ENTRY_ID}={nama_p.replace(' ', '+')}&submit=Submit"
        
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

# 7. LOAD DATA
log_pns = process_log(fetch_data(URL_PNS), tgl_pilihan)
log_pppk = process_log(fetch_data(URL_PPPK), tgl_pilihan)
combined_log = {**log_pns, **log_pppk}

# 8. TABS
tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA PEGAWAI", "👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])

with tab_all:
    render_list(combined_log, MASTER_ALL_HIERARCHY, sort_priority=True)

with tab_pns:
    render_list(log_pns, MASTER_PNS, sort_priority=False)

with tab_pppk:
    render_list(log_pppk, MASTER_PPPK, sort_priority=False)

# 9. LOGIKA JAM & REFRESH 60 DETIK
while True:
    wita_tick = datetime.now() + timedelta(hours=8)
    placeholder_header.markdown(f"""
        <div class="header-jam">
            <div class="clock-text">{wita_tick.strftime("%H:%M:%S")}</div>
            <div class="running-text-container">
                <div class="running-text">
                    ABSENSI KPU Kabupaten Hulu Sungai Selatan &nbsp; • &nbsp; 
                    <span class="highlight">Silahkan Cek Kehadiran hari ini yaa, yang belum absen bisa klik di bagian Nama masing-masing</span> &nbsp; • &nbsp; 
                    ABSENSI KPU Kabupaten Hulu Sungai Selatan
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if wita_tick.second == 0:
        st.rerun()
    time.sleep(1)
