import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: FOKUS PADA CENTERING SEMUA ELEMEN
st.markdown("""
    <style>
    .stApp { background-color: #2d0a0a; color: #ffffff; }
    
    /* Header Jam Center */
    .header-jam { text-align: center; padding: 20px 0; }
    .clock-text { font-size: 70px; font-weight: bold; color: #ffffff; text-shadow: 0 0 20px rgba(255,255,255,0.6); }
    
    /* Memaksa elemen input dan button Streamlit ke tengah */
    .stDateInput, .stButton {
        display: flex;
        justify-content: center;
    }
    
    /* Styling Tombol CARI DATA agar tetap Orange dan Lebar */
    div.stButton > button { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; 
        width: 100% !important; 
        max-width: 450px !important; /* Lebar maksimal tombol */
        height: 60px !important; 
        font-size: 20px !important; 
        font-weight: 800 !important; 
        border-radius: 15px !important;
        border: 1px solid #fb923c !important;
        box-shadow: 0 0 15px rgba(234, 88, 12, 0.4) !important;
        margin-top: 10px;
    }

    /* Tabs Center */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 5px; border: none !important; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #4c0519 !important; border-radius: 12px 12px 0 0 !important; 
        padding: 12px 40px !important; color: #fca5a5 !important;
    }
    .stTabs [aria-selected="true"] { background-color: #f97316 !important; color: #ffffff !important; }

    /* Baris Pegawai Center */
    .row-container {
        display: flex; align-items: center;
        background: linear-gradient(90deg, #4c0519 0%, #7f1d1d 100%);
        padding: 15px 25px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #991b1b;
        max-width: 1100px; margin-left: auto; margin-right: auto;
    }

    .col-nama { flex: 4; font-size: 18px; font-weight: 700; }
    .col-nama a { color: #fecaca; text-decoration: none; display: block; width: 100%; }
    
    .col-data-wrap { 
        flex: 5; display: flex; justify-content: space-around; 
        text-align: center; border-left: 1px solid #991b1b; padding: 0 30px;
    }
    .val-v { font-size: 16px; font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIKA WAKTU & DATA
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="header-jam"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# --- BAGIAN INI YANG DIPERBAIKI AGAR CENTER ---
# Menggunakan kolom dengan proporsi seimbang agar elemen di tengah (col_mid)
col_left, col_mid, col_right = st.columns([1, 1.5, 1])

with col_mid:
    tgl_pilihan = st.date_input("Pilih Tanggal", wita_now.date(), label_visibility="collapsed")
    if st.button("🔍 CARI DATA"):
        st.rerun()
# ----------------------------------------------

# Master Data & URL tetap sama
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

def render_list(df, master, form_url):
    today = tgl_pilihan.strftime('%d/%m/%Y')
    log = {}
    if not df.empty:
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if today in ts:
                try:
                    dt = pd.to_datetime(ts, dayfirst=True)
                    nama, jam = str(r.iloc[1]).strip(), dt.time()
                    if nama not in log:
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam.hour < 9 else "TERLAMBAT"}
                    elif jam.hour >= 16: log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.markdown("<br>", unsafe_allow_html=True)
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "ALPA"})
        clr = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        link = f"{form_url}?entry.{E_ID}={p.replace(' ', '+')}&submit=Submit"
        
        st.markdown(f"""
        <div class="row-container">
            <div class="col-nama"><a href="{link}" target="_self">{i}. {p.split(',')[0]}</a></div>
            <div class="col-data-wrap">
                <div class="item-box"><div class="label-k">Pagi</div><div class="val-v">{d['m']}</div></div>
                <div class="item-box"><div class="label-k">Sore</div><div class="val-v">{d['p']}</div></div>
                <div class="item-box"><div class="label-k">Ket</div><div style="color:{clr}; font-weight:900;">{d['k']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 4. TABS
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1:
    res = requests.get(f"{URL_PNS}&nc={random.random()}")
    render_list(pd.read_csv(StringIO(res.text)) if res.status_code==200 else pd.DataFrame(), MASTER_DATA["PNS"], FORM_PNS)
with tab2:
    res = requests.get(f"{URL_PPPK}&nc={random.random()}")
    render_list(pd.read_csv(StringIO(res.text)) if res.status_code==200 else pd.DataFrame(), MASTER_DATA["PPPK"], FORM_PPPK)

# Auto Refresh 30 detik
time.sleep(30)
st.rerun()
