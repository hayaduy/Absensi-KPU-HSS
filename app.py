import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: SEMUA TENGAH & SIMETRIS ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Header & Clock */
    .header-container { text-align: center; padding: 30px 0; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 0 0 40px 40px; margin-bottom: 40px; border-bottom: 3px solid #38bdf8; }
    .main-title { font-size: 20px; font-weight: 800; color: #38bdf8; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
    .clock-text { font-size: clamp(40px, 8vw, 65px); font-family: 'JetBrains Mono', monospace; font-weight: bold; color: #ffffff; text-shadow: 0 0 15px rgba(56, 189, 248, 0.6); }
    
    /* KONTROL TENGAH (TANGGAL & CARI DATA) */
    .center-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        margin-bottom: 40px;
    }
    
    /* Styling Input Tanggal */
    div[data-testid="stDateInput"] { width: 320px !important; margin: 0 auto !important; }
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] > div { border-radius: 12px !important; background: #1e293b !important; }

    /* Tombol CARI DATA (Fix Center & Big) */
    div.stButton { text-align: center; }
    div.stButton > button:first-child { 
        background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%) !important; 
        color: white !important; width: 320px !important; height: 60px !important; 
        font-size: 18px !important; font-weight: 800 !important; border-radius: 15px !important;
        margin: 20px auto !important; display: block !important; border: none !important;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.4) !important;
    }

    /* TABS CENTERED */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #1e293b !important; border-radius: 10px 10px 0 0 !important; 
        padding: 12px 30px !important; font-size: clamp(14px, 4vw, 18px) !important; font-weight: 700 !important;
    }
    .stTabs [aria-selected="true"] { background-color: #38bdf8 !important; color: #0f172a !important; }

    /* LAYOUT KARTU & TOMBOL ABSEN (Symmetric) */
    .presence-container {
        display: flex;
        align-items: stretch; /* Paksa tinggi sama */
        margin-bottom: 15px;
        gap: 10px;
    }

    .presence-card { 
        background: #1e293b; padding: 20px; border-radius: 20px;
        border: 1px solid #334155; display: flex; align-items: center; 
        justify-content: space-between; flex-grow: 1;
    }

    .user-name { font-size: clamp(14px, 4vw, 18px); font-weight: 700; color: #f8fafc; flex: 1.5; }
    .stats-info { flex: 2; display: flex; justify-content: space-around; text-align: center; border-left: 1px solid #334155; padding-left: 10px; }
    .stat-label { font-size: 9px; color: #94a3b8; text-transform: uppercase; margin-bottom: 4px; }
    .stat-val { font-size: clamp(12px, 3.5vw, 16px); font-weight: 700; color: #f1f5f9; }
    
    /* TOMBOL ABSEN (High Symmetric) */
    .btn-container { width: 140px; display: flex; }
    .btn-container button {
        background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%) !important; 
        color: white !important; height: 100% !important; width: 100% !important;
        border-radius: 20px !important; font-weight: 800 !important; font-size: 16px !important;
        border: none !important; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3) !important;
        margin: 0 !important;
    }

    /* RESPONSIVE HP */
    @media (max-width: 768px) {
        .presence-container { flex-direction: column; align-items: center; }
        .presence-card { width: 100%; flex-direction: column; text-align: center; gap: 15px; }
        .stats-info { border: none; padding-left: 0; width: 100%; border-top: 1px solid #334155; padding-top: 15px; }
        .btn-container { width: 100%; height: 60px !important; }
        div[data-testid="stDateInput"], div.stButton > button:first-child { width: 90% !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATA ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# --- HEADER ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">KPU KABUPATEN HULU SUNGAI SELATAN</div>
        <div class="clock-text">{wita_now.strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

# --- CENTERED CONTROLS ---
tgl_pilihan = st.date_input("Tanggal", wita_now.date())
if st.button("🔍 CARI DATA"): 
    st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        return pd.read_csv(StringIO(res.text)).dropna(subset=[pd.read_csv(StringIO(res.text)).columns[0]])
    except: return pd.DataFrame()

def direct_submit(form_url, nama):
    import urllib.parse
    enc_nama = urllib.parse.quote(nama)
    final_url = f"{form_url}?entry.{E_ID}={enc_nama}&submit=Submit"
    st.markdown(f"""<meta http-equiv="refresh" content="0;URL='{final_url}'">""", unsafe_allow_html=True)
    st.info(f"🔄 Memproses Absen {nama.split(',')[0]}...")
    time.sleep(2)

def render_list(df, master, form_url, prefix):
    t_batas, t_pulang = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        t_str, t_str_alt = tgl_pilihan.strftime('%d/%m/%Y'), tgl_pilihan.strftime('%Y-%m-%d')
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if t_str in ts or t_str_alt in ts:
                try:
                    dt = pd.to_datetime(ts, dayfirst=True)
                    nama, jam = str(r.iloc[1]).strip(), dt.time()
                    if nama not in log:
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_batas else "TERLAMBAT"}
                    elif jam >= t_pulang: log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.markdown("<br>", unsafe_allow_html=True)
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "ALPA"})
        clr_status = "#22c55e" if d["k"]=="HADIR" else "#f59e0b" if d["k"]=="TERLAMBAT" else "#ef4444"
        
        # HTML + Button Container
        st.markdown(f"""
        <div class="presence-container">
            <div class="presence-card">
                <div class="user-name">{i}. {p.split(',')[0]}</div>
                <div class="stats-info">
                    <div class="stat-box"><div class="stat-label">Pagi</div><div class="stat-val">{d['m']}</div></div>
                    <div class="stat-box"><div class="stat-label">Sore</div><div class="stat-val">{d['p']}</div></div>
                    <div class="stat-box"><div class="stat-label">Keterangan</div><div class="stat-val" style="color:{clr_status}">{d['k']}</div></div>
                </div>
            </div>
            <div class="btn-container" id="btn-target-{prefix}-{i}">
        """, unsafe_allow_html=True)
        
        # Streamlit Button di dalam slot
        if st.button("ABSEN", key=f"btn_{prefix}_{i}"):
            direct_submit(form_url, p)
            
        st.markdown("</div></div>", unsafe_allow_html=True)

# --- TABEL DATA ---
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")

st.markdown("<br><br>", unsafe_allow_html=True)
