import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# --- CSS: REPLIKA PERSIS IMAGE_94E40C ---
st.markdown("""
    <style>
    /* Background Maroon Gelap */
    .stApp { background-color: #2d0a0a; color: #ffffff; }
    
    /* Header Section */
    .header-container { text-align: center; padding: 20px 0; margin-bottom: 20px; }
    .clock-text { font-size: 60px; font-family: 'JetBrains Mono', monospace; font-weight: bold; color: #ffffff; text-shadow: 0 0 15px rgba(255, 255, 255, 0.8); }
    
    /* Control Center (Tanggal & Cari Data) */
    .stDateInput { width: 300px !important; margin: 0 auto !important; }
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] > div { border-radius: 10px !important; background: #1e1e1e !important; color: white !important; }
    
    /* Tombol CARI DATA (Pasti Tengah & Gede) */
    .stButton { display: flex; justify-content: center; }
    div.stButton > button:first-child { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; width: 450px !important; height: 70px !important; 
        font-size: 22px !important; font-weight: 800 !important; border-radius: 25px !important;
        margin: 20px auto !important; border: 1px solid #fb923c !important;
        box-shadow: 0 0 20px rgba(234, 88, 12, 0.6) !important;
    }

    /* TABS (Gaya Gambar) */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 5px; border: none !important; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #4c0519 !important; border-radius: 12px 12px 0 0 !important; 
        padding: 12px 35px !important; font-size: 15px !important; font-weight: 700 !important;
        color: #fca5a5 !important; border: none !important;
    }
    .stTabs [aria-selected="true"] { background-color: #f97316 !important; color: #ffffff !important; }

    /* LAYOUT BARIS (Satu Garis Lurus) */
    .row-absensi {
        display: flex;
        flex-direction: row;
        align-items: center;
        background: linear-gradient(90deg, #4c0519 0%, #7f1d1d 100%);
        padding: 5px 20px;
        border-radius: 15px;
        margin-bottom: 10px;
        border: 1px solid #991b1b;
        justify-content: space-between;
        min-height: 70px;
    }

    .col-nama { flex: 3; font-size: 16px; font-weight: 700; color: #fecaca; text-align: left; }
    
    .col-stats { 
        flex: 5; display: flex; justify-content: space-around; 
        text-align: center; border-left: 1px solid #991b1b; padding: 0 20px;
    }
    .stat-item { flex: 1; }
    .label-kecil { font-size: 9px; color: #fca5a5; text-transform: uppercase; margin-bottom: 2px; }
    .val-besar { font-size: 15px; font-weight: 800; color: #ffffff; }
    .status-text { font-size: 15px; font-weight: 800; }

    /* TOMBOL ABSEN SAMPING (Simetris) */
    .col-btn { flex: 2; display: flex; justify-content: flex-end; height: 100%; }
    div[data-testid="column"]:nth-child(2) button {
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; height: 55px !important; width: 100% !important;
        border-radius: 15px !important; font-weight: 800 !important; font-size: 16px !important;
        border: 1px solid #fb923c !important; margin: 0 !important;
        box-shadow: 0 4px 10px rgba(249, 115, 22, 0.3) !important;
    }

    /* RESPONSIVE MOBILE */
    @media (max-width: 800px) {
        .row-absensi { flex-direction: column; padding: 20px; text-align: center; gap: 15px; }
        .col-nama { flex: 100%; font-size: 18px; text-align: center; }
        .col-stats { flex: 100%; border-left: none; border-top: 1px solid #991b1b; padding-top: 15px; width: 100%; }
        .col-btn { flex: 100%; width: 100%; }
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

# --- HEADER ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="header-container"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

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
    st.info(f"🚀 Memproses Absen {nama.split(',')[0]}...")
    time.sleep(2)

def render_list(df, master, form_url, prefix):
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
        
        # BARIS SEJAJAR: Nama | Pagi | Sore | Ket | [ABSEN]
        st.markdown(f"""
        <div class="row-absensi">
            <div class="col-nama">{i}. {p.split(',')[0]}</div>
            <div class="col-stats">
                <div class="stat-item"><div class="label-kecil">Pagi</div><div class="val-besar">{d['m']}</div></div>
                <div class="stat-item"><div class="label-kecil">Sore</div><div class="val-besar">{d['p']}</div></div>
                <div class="stat-item"><div class="label-kecil">Ket</div><div class="status-text" style="color:{clr_status}">{d['k']}</div></div>
            </div>
            <div class="col-btn">
        """, unsafe_allow_html=True)
        
        if st.button("ABSEN", key=f"btn_{prefix}_{i}"):
            direct_submit(form_url, p)
            
        st.markdown("</div></div>", unsafe_allow_html=True)

# --- TABEL DATA ---
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")

st.markdown("<br><br>", unsafe_allow_html=True)
