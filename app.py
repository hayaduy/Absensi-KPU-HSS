import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# Konfigurasi Halaman (WAJIB DI ATAS)
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# --- CSS FIX: AGAR TAMPILAN MUNCUL & SEJAJAR ---
st.markdown("""
    <style>
    /* Background Utama */
    .stApp { background-color: #2d0a0a; color: #ffffff; }
    
    /* Jam Digital Besar */
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { font-size: 60px; font-weight: bold; color: #ffffff; text-shadow: 0 0 15px rgba(255,255,255,0.3); }
    
    /* Tombol Cari Data */
    div[data-testid="stDateInput"] { width: 250px !important; margin: 0 auto !important; }
    .stButton > button { margin: 0 auto; }

    /* Layout Baris (Card) */
    .row-card {
        background: linear-gradient(90deg, #450a0a 0%, #630a0a 100%);
        border: 1px solid #7f1d1d;
        border-radius: 10px;
        padding: 12px 20px;
        display: flex;
        align-items: center;
        width: 100%;
        margin-bottom: 2px; /* Jarak antar baris */
    }

    .nama-box { flex: 2; font-size: 16px; font-weight: bold; color: #fecaca; }
    
    .data-section { 
        flex: 3; 
        display: flex; 
        justify-content: space-around; 
        border-left: 1px solid #991b1b;
        padding: 0 15px;
    }
    
    .data-item { text-align: center; }
    .data-label { font-size: 9px; color: #fca5a5; text-transform: uppercase; }
    .data-val { font-size: 15px; font-weight: 800; color: #ffffff; }

    /* Tombol ABSEN */
    div[data-testid="column"] .stButton > button {
        background: linear-gradient(180deg, #ea580c 0%, #9a3412 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #fb923c !important;
        height: 45px !important;
        width: 100% !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
    }

    /* Tabs Style */
    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #450a0a !important; 
        color: #fca5a5 !important; 
        border-radius: 10px 10px 0 0 !important;
        padding: 10px 30px !important;
    }
    .stTabs [aria-selected="true"] { background-color: #ea580c !important; color: white !important; }
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

# --- LOGIKA AUTO REFRESH (Setiap 30 Detik) ---
# Trik ini membuat halaman update otomatis tanpa interaksi user
st.empty() 
if 'count' not in st.session_state:
    st.session_state.count = 0

# --- JAM ATAS ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="header-jam"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# --- CARI DATA ---
tgl_pilihan = st.date_input("Tgl", wita_now.date(), label_visibility="collapsed")
if st.button("🔍 CARI DATA", use_container_width=True):
    st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=5)
        return pd.read_csv(StringIO(res.text))
    except: return pd.DataFrame()

def direct_submit(form_url, nama):
    import urllib.parse
    enc_nama = urllib.parse.quote(nama)
    # Trik Redirect ke GForm dan OTOMATIS KEMBALI dalam 2 detik menggunakan URL redirect
    # Catatan: Karena Google Form tidak mendukung redirect balik secara native, 
    # kita gunakan meta refresh ganda atau instruksi ke user.
    final_url = f"{form_url}?entry.{E_ID}={enc_nama}&submit=Submit"
    
    st.markdown(f"### 🔄 Sedang Mengabsen {nama.split(',')[0]}...")
    st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{final_url}\'">', unsafe_allow_html=True)
    time.sleep(3)
    st.rerun()

def render_list(df, master, form_url, prefix):
    t_limit, t_pulang = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        t_str, t_str_alt = tgl_pilihan.strftime('%d/%m/%Y'), tgl_pilihan.strftime('%Y-%m-%d')
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if t_str in ts or t_str_alt in ts:
                try:
                    dt = pd.to_datetime(ts)
                    nama, jam = str(r.iloc[1]).strip(), dt.time()
                    if nama not in log:
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}
                    elif jam >= t_pulang: log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.markdown("<br>", unsafe_allow_html=True)
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "ALPA"})
        clr_status = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        
        # Menggunakan columns agar tombol ABSEN bisa diklik (Streamlit Button tidak jalan di dalam HTML murni)
        col_data, col_btn = st.columns([85, 15])
        
        with col_data:
            st.markdown(f"""
                <div class="row-card">
                    <div class="nama-box">{i}. {p.split(',')[0]}</div>
                    <div class="data-section">
                        <div class="data-item"><div class="data-label">Pagi</div><div class="data-val">{d['m']}</div></div>
                        <div class="data-item"><div class="data-label">Sore</div><div class="data-val">{d['p']}</div></div>
                        <div class="data-item"><div class="data-label">Ket</div><div style="color:{clr_status}; font-weight:900; font-size:14px;">{d['k']}</div></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with col_btn:
            if st.button("ABSEN", key=f"{prefix}_{i}"):
                direct_submit(form_url, p)

# --- TABS ---
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1:
    data_pns = fetch_data(URL_PNS)
    render_list(data_pns, MASTER_DATA["PNS"], FORM_PNS, "pns")

with tab2:
    data_pppk = fetch_data(URL_PPPK)
    render_list(data_pppk, MASTER_DATA["PPPK"], FORM_PPPK, "pppk")

# Script Auto Refresh Halaman setiap 60 detik agar data selalu update
time.sleep(60)
st.rerun()
