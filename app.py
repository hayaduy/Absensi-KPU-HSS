import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: TETAP CENTER & MAROON
st.markdown("""
    <style>
    .stApp { background-color: #2d0a0a; color: #ffffff; }
    
    .header-jam { text-align: center; padding: 20px 0; }
    .clock-text { font-size: 70px; font-weight: bold; color: #ffffff; text-shadow: 0 0 20px rgba(255,255,255,0.6); }
    
    /* Input & Tombol Cari Center */
    div[data-testid="stDateInput"] { width: 300px !important; margin: 0 auto !important; }
    div[data-testid="stDateInput"] label { display: none; }
    
    div.stButton { display: flex; justify-content: center; width: 100%; }
    div.stButton > button { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; width: 450px !important; height: 60px !important; 
        font-size: 20px !important; font-weight: 800 !important; border-radius: 15px !important;
        border: 1px solid #fb923c !important; box-shadow: 0 0 15px rgba(234, 88, 12, 0.4) !important;
    }

    /* Tabs Center */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 5px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #4c0519 !important; border-radius: 12px 12px 0 0 !important; 
        padding: 12px 40px !important; color: #fca5a5 !important;
    }
    .stTabs [aria-selected="true"] { background-color: #f97316 !important; color: #ffffff !important; }

    /* Baris Pegawai */
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
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# 4. TAMPILAN HEADER
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="header-jam"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    tgl_pilihan = st.date_input("Tgl", wita_now.date(), label_visibility="collapsed")
    if st.button("🔍 CARI DATA", use_container_width=True):
        st.rerun()

def render_list(df, master, form_url):
    today = tgl_pilihan.strftime('%d/%m/%Y')
    log = {}
    if not df.empty:
        # Menggunakan loop sederhana untuk memetakan nama yang sudah absen
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if today in ts:
                nama = str(r.iloc[1]).strip()
                log[nama] = "OK"

    st.markdown("<br>", unsafe_allow_html=True)
    for i, p in enumerate(sorted(master), 1):
        status_absen = log.get(p.strip(), "--:--")
        clr = "#4ade80" if status_absen == "OK" else "#f87171"
        
        # PERUBAHAN DISINI: target="_self" agar terbuka di halaman yang sama
        # Menambahkan parameter usp=pp_url untuk mencoba memicu navigasi balik (opsional)
        link = f"{form_url}?entry.{E_ID}={p.replace(' ', '+')}&submit=Submit"
        
        st.markdown(f"""
        <div class="row-container">
            <div class="col-nama">
                <a href="{link}" target="_self">{i}. {p.split(',')[0]}</a>
            </div>
            <div class="col-data-wrap">
                <div class="item-box"><div class="val-v">KLIK NAMA UNTUK ABSEN</div></div>
                <div class="item-box"><div style="color:{clr}; font-weight:900;">{ "SUDAH" if status_absen=="OK" else "BELUM" }</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 5. TABS
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1:
    res_pns = requests.get(f"{URL_PNS}&nc={random.random()}")
    render_list(pd.read_csv(StringIO(res_pns.text)) if res_pns.status_code==200 else pd.DataFrame(), MASTER_DATA["PNS"], FORM_PNS)
with tab2:
    res_pppk = requests.get(f"{URL_PPPK}&nc={random.random()}")
    render_list(pd.read_csv(StringIO(res_pppk.text)) if res_pppk.status_code==200 else pd.DataFrame(), MASTER_DATA["PPPK"], FORM_PPPK)

# Refresh otomatis agar jam update
time.sleep(10)
st.rerun()
