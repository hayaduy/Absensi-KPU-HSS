import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: MODERN UI DENGAN LABEL PAGI & SORE ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Header & Clock */
    .header-container { text-align: center; padding: 25px 0; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 0 0 35px 35px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); border-bottom: 2px solid #38bdf8; }
    .main-title { font-size: 20px; font-weight: 800; color: #38bdf8; letter-spacing: 2px; text-transform: uppercase; }
    .clock-text { font-size: 55px; font-family: 'JetBrains Mono', monospace; font-weight: bold; color: #ffffff; text-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
    
    /* Input & Refresh Area */
    div[data-testid="stDateInput"] label { display: none; }
    .stButton > button { border-radius: 12px !important; transition: all 0.3s ease !important; }
    
    /* Refresh Button */
    div.stButton > button:first-child { 
        background: #1e293b !important; color: #38bdf8 !important; height: 45px !important; 
        border: 1px solid #38bdf8 !important; font-weight: bold !important;
    }

    /* Card Design */
    .presence-card { 
        background: #1e293b; padding: 18px; border-radius: 20px; margin-bottom: 12px; 
        border: 1px solid #334155; display: flex; align-items: center; justify-content: space-between;
    }
    .user-info { flex: 2.5; }
    .user-name { font-size: 17px; font-weight: 700; color: #f8fafc; }
    
    .stats-info { flex: 2; display: flex; justify-content: space-around; text-align: center; border-left: 1px solid #334155; margin-left: 15px; }
    .stat-box { flex: 1; }
    .stat-label { font-size: 9px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 3px; }
    .stat-val { font-size: 15px; font-weight: 700; color: #f1f5f9; }
    
    /* Responsive Mobile */
    @media (max-width: 768px) {
        .presence-card { flex-direction: column; text-align: center; }
        .stats-info { border: none; margin: 15px 0; width: 100%; border-top: 1px solid #334155; padding-top: 10px; }
        .btn-container { width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA PEGAWAI ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

# Config URLs
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# --- LOGIKA WAKTU & LABEL ---
wita_now = datetime.now() + timedelta(hours=8)
is_pagi_time = wita_now.hour < 16
label_absen = "ABSEN PAGI" if is_pagi_time else "ABSEN SORE"
color_btn = "#f59e0b" if is_pagi_time else "#3b82f6"

st.markdown(f"""
    <div class="header-container">
        <div class="main-title">KPU KABUPATEN HULU SUNGAI SELATAN</div>
        <div class="clock-text">{wita_now.strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 1.5, 1])
with c2:
    tgl_pilihan = st.date_input("Tanggal", wita_now.date())
    if st.button("🔄 PERBARUI DATA"): st.rerun()

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
    st.info(f"🚀 Memproses {label_absen} {nama.split(',')[0]}...")
    time.sleep(2)

def render_list(df, master, form_url, prefix):
    t_batas = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("16:00", "%H:%M").time()
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
        
        with st.container():
            col_info, col_btn = st.columns([5, 2])
            with col_info:
                st.markdown(f"""
                <div class="presence-card">
                    <div class="user-info">
                        <div class="user-name">{i}. {p.split(',')[0]}</div>
                    </div>
                    <div class="stats-info">
                        <div class="stat-box"><div class="stat-label">Pagi</div><div class="stat-val">{d['m']}</div></div>
                        <div class="stat-box"><div class="stat-label">Sore</div><div class="stat-val">{d['p']}</div></div>
                        <div class="stat-box"><div class="stat-label">Ket</div><div class="stat-val" style="color:{clr_status}">{d['k']}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button(f"{label_absen}", key=f"btn_{prefix}_{i}"):
                    direct_submit(form_url, p)
                # Suntik CSS tombol khusus untuk kolom absen
                st.markdown(f"""
                    <style>
                    div[data-testid="column"]:nth-child(2) button {{
                        background: {color_btn} !important; color: white !important;
                        height: 55px !important; margin-top: 12px !important;
                        font-weight: 800 !important; width: 100% !important;
                        box-shadow: 0 4px 10px {color_btn}44 !important;
                    }}
                    </style>
                """, unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])
with tab1: render_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")

st.markdown("<br><br>", unsafe_allow_html=True)
