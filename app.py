import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: REPLIKA PERSIS TOTAL (IMAGE_94E40C) ---
st.markdown("""
    <style>
    /* Background & Global Font */
    .stApp { background-color: #2d0a0a; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
    
    /* Header Jam */
    .clock-container { text-align: center; padding: 20px 0; }
    .clock-text { font-size: 60px; font-weight: bold; color: #ffffff; text-shadow: 0 0 10px rgba(255,255,255,0.5); }
    
    /* Center Controls */
    div[data-testid="stDateInput"] { width: 300px !important; margin: 0 auto !important; }
    div[data-testid="stDateInput"] label { display: none; }
    
    /* Tombol CARI DATA Gede & Tengah */
    .stButton { display: flex; justify-content: center; }
    div.stButton > button:first-child { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; width: 400px !important; height: 60px !important; 
        font-size: 20px !important; font-weight: 800 !important; border-radius: 20px !important;
        margin: 10px auto !important; border: 1px solid #fb923c !important;
        box-shadow: 0 0 15px rgba(234, 88, 12, 0.5) !important;
    }

    /* TABS Gaya Gambar */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 5px; border: none !important; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #4c0519 !important; border-radius: 10px 10px 0 0 !important; 
        padding: 10px 30px !important; font-size: 14px !important; font-weight: 700 !important;
        color: #fca5a5 !important; border: none !important;
    }
    .stTabs [aria-selected="true"] { background-color: #f97316 !important; color: #ffffff !important; }

    /* --- LAYOUT SATU BARIS (IDENTIK GAMBAR) --- */
    .row-wrapper {
        display: flex;
        flex-direction: row;
        align-items: center;
        background: linear-gradient(90deg, #4c0519 0%, #7f1d1d 100%);
        padding: 5px 15px;
        border-radius: 12px;
        margin-bottom: 8px;
        border: 1px solid #991b1b;
        width: 100%;
        min-height: 60px;
    }

    .col-nama { flex: 3; font-size: 16px; font-weight: 700; color: #fecaca; }
    
    .col-data { 
        flex: 5; display: flex; justify-content: space-around; 
        text-align: center; border-left: 1px solid #991b1b; padding: 0 15px;
    }
    .data-box { flex: 1; }
    .label-k { font-size: 8px; color: #fca5a5; text-transform: uppercase; margin-bottom: 1px; }
    .val-k { font-size: 14px; font-weight: 800; color: #ffffff; }

    /* TOMBOL ABSEN DI DALAM KANAN */
    .col-btn-wrap { flex: 1.5; display: flex; justify-content: flex-end; }
    div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; height: 40px !important; width: 100% !important;
        border-radius: 10px !important; font-weight: 800 !important; font-size: 14px !important;
        border: 1px solid #fb923c !important; margin: 0 !important;
    }

    /* Mobile Responsive */
    @media (max-width: 850px) {
        .row-wrapper { flex-direction: column; padding: 15px; text-align: center; }
        .col-nama { margin-bottom: 10px; width: 100%; }
        .col-data { border-left: none; border-top: 1px solid #991b1b; padding-top: 10px; width: 100%; margin-bottom: 10px; }
        .col-btn-wrap { width: 100%; }
        div.stButton > button:first-child { width: 90% !important; }
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

# --- HEADER JAM ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="clock-container"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# --- CONTROLS ---
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
    st.info(f"🚀 Memproses Absen {nama.split(',')[0]}...")
    time.sleep(2)

def render_row(df, master, form_url, prefix):
    t_limit, t_pulang = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
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
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}
                    elif jam >= t_out: log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.markdown("<br>", unsafe_allow_html=True)
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "ALPA"})
        clr_status = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        
        # SATU BARIS PENUH (IDENTIK GAMBAR)
        st.markdown(f"""
        <div class="row-wrapper">
            <div class="col-nama">{i}. {p.split(',')[0]}</div>
            <div class="col-data">
                <div class="data-box"><div class="label-k">Pagi</div><div class="val-k">{d['m']}</div></div>
                <div class="data-box"><div class="label-k">Sore</div><div class="val-k">{d['p']}</div></div>
                <div class="data-box"><div class="label-k">Ket</div><div style="color:{clr_status}; font-weight:800; font-size:14px;">{d['k']}</div></div>
            </div>
            <div class="col-btn-wrap">
        """, unsafe_allow_html=True)
        
        if st.button("ABSEN", key=f"btn_{prefix}_{i}"):
            direct_submit(form_url, p)
            
        st.markdown("</div></div>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_row(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_row(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")
