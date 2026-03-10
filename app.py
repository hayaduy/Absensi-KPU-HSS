import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# Konfigurasi Halaman
st.set_page_config(page_title="KPU HSS Presence", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: MODERN & MINIMALIST UI ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Header & Clock */
    .header-container { text-align: center; padding: 20px 0; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 0 0 30px 30px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .main-title { font-size: 24px; font-weight: 800; letter-spacing: 1px; color: #38bdf8; margin-bottom: 5px; }
    .clock-text { font-size: 48px; font-family: 'Courier New', Courier, monospace; font-weight: bold; color: #f8fafc; }
    
    /* Date & Scan Section */
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] > div { border-radius: 15px !important; background: #1e293b !important; border: 1px solid #334155 !important; }
    
    .stButton > button {
        border-radius: 15px !important; width: 100% !important; transition: all 0.3s ease !important;
        font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 1px !important;
    }
    
    /* Scan Button Style */
    div.stButton > button:first-child { background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%) !important; color: white !important; height: 55px !important; border: none !important; font-size: 18px !important; }
    div.stButton > button:first-child:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(217, 119, 6, 0.4); }

    /* Table & Card Container */
    .presence-row { display: flex; align-items: center; justify-content: space-between; background: #1e293b; padding: 15px 20px; border-radius: 18px; margin-bottom: 12px; border: 1px solid #334155; }
    .name-section { flex: 3; }
    .name-text { font-size: 16px; font-weight: 600; color: #f1f5f9; }
    .info-section { flex: 2; display: flex; justify-content: space-around; text-align: center; }
    .info-box { flex: 1; }
    .info-label { font-size: 10px; color: #94a3b8; text-transform: uppercase; margin-bottom: 2px; }
    .info-val { font-size: 14px; font-weight: 700; color: #cbd5e1; }
    
    /* Action Buttons P & S */
    .btn-action { width: 50px !important; height: 50px !important; border-radius: 12px !important; font-size: 18px !important; }
    
    /* Responsive Fix for Mobile */
    @media (max-width: 768px) {
        .presence-row { flex-direction: column; text-align: center; padding: 20px; }
        .name-section { margin-bottom: 15px; }
        .info-section { width: 100%; margin-bottom: 15px; }
        .action-section { display: flex; gap: 10px; width: 100%; }
        .btn-action { flex: 1; height: 55px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATA ---
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

# --- HEADER SECTION ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f"""
    <div class="header-container">
        <div class="main-title">KPU HULU SUNGAI SELATAN</div>
        <div class="clock-text">{wita_now.strftime('%H:%M:%S')}</div>
    </div>
    """, unsafe_allow_html=True)

# --- CONTROLS SECTION ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    tgl_pilihan = st.date_input("Pilih Tanggal", wita_now.date())
    if st.button("🚀 SCAN DATA SEKARANG"): st.rerun()

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
    st.info(f"🔄 Redirecting {nama.split(',')[0]} to Secure Submit...")
    time.sleep(2)

def render_modern_list(df, master, form_url, prefix):
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
        clr = "#22c55e" if d["k"]=="HADIR" else "#f59e0b" if d["k"]=="TERLAMBAT" else "#ef4444"
        
        # Row Container
        with st.container():
            col_data, col_actions = st.columns([5, 1.5])
            
            with col_data:
                st.markdown(f"""
                <div class="presence-row">
                    <div class="name-section">
                        <div class="name-text">{i}. {p.split(',')[0]}</div>
                    </div>
                    <div class="info-section">
                        <div class="info-box"><div class="info-label">In</div><div class="info-val">{d['m']}</div></div>
                        <div class="info-box"><div class="info-label">Out</div><div class="info-val">{d['p']}</div></div>
                        <div class="info-box"><div class="info-label">Status</div><div class="info-val" style="color:{clr}">{d['k']}</div></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_actions:
                btn_p, btn_s = st.columns(2)
                with btn_p:
                    if st.button("P", key=f"p_{prefix}_{i}"): direct_submit(form_url, p)
                with btn_s:
                    if st.button("S", key=f"s_{prefix}_{i}"): direct_submit(form_url, p)

# --- TABS SECTION ---
st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_modern_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_modern_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")

st.markdown("""<div style="text-align:center; color:#475569; padding:30px; font-size:12px;">© 2026 KPU Kabupaten Hulu Sungai Selatan</div>""", unsafe_allow_html=True)
