import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Monitoring Absensi KPU HSS", page_icon="👻", layout="wide")

# 2. DATABASE NIP & JABATAN (LENGKAP)
# Sistem akan otomatis mengambil NIP & Jabatan saat nama diklik
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["197103031993031005", "SEKRETARIS"],
    "Wawan Setiawan, SH": ["198105252009041001", "KASUBBAG TEKNIS"],
    "Ineke Setiyaningsih, S.Sos": ["197505242006042017", "KASUBBAG KEUANGAN"],
    "Farah Agustina Setiawati, SH": ["198408012009122003", "KASUBBAG HUKUM"],
    "Rusma Ariati, SE": ["197904222008012018", "KASUBBAG UMUM"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN OPERASIONAL"],
    # Pegawai lain akan otomatis pakai NIP '-' dan Jabatan 'STAF' jika belum didaftarkan di sini
}

MASTER_PNS = [
    "Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", 
    "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", 
    "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", 
    "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", 
    "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", 
    "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."
]
MASTER_PPPK = [
    "Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", 
    "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", 
    "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", 
    "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"
]
MASTER_ALL = MASTER_PNS + MASTER_PPPK

# 3. CSS MODERN
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
    .block-container { padding-top: 1rem; max-width: 1000px !important; margin: 0 auto; }
    .clock-text { font-size: 70px; font-weight: 900; text-align: center; color: white; text-shadow: 0 0 20px #f97316; }
    div.stButton > button {
        background-color: rgba(249, 115, 22, 0.1) !important; color: #fecaca !important;
        border: 1px solid rgba(249, 115, 22, 0.3) !important; font-weight: bold !important;
        text-align: left !important; padding-left: 20px !important; height: 55px !important; border-radius: 12px !important;
    }
    div.stButton > button:hover { background-color: rgba(249, 115, 22, 0.3) !important; border: 1px solid #f97316 !important; color: white !important; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; }
    .val-v { font-size: 18px; font-weight: 800; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNGSI CORE
def get_wita():
    return datetime.utcnow() + timedelta(hours=8)

def kirim_absen_silent(nama, is_pns):
    target = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse" if is_pns else "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
    
    # Ambil NIP & Jabatan otomatis dari database di atas
    info = DATABASE_INFO.get(nama, ["-", "STAF / ANGGOTA"])
    
    payload = {
        "entry.960346359": nama,
        "entry.468881973": info[0],
        "entry.159009649": info[1]
    }
    try:
        r = requests.post(target, data=payload, timeout=10)
        return r.status_code == 200
    except: return False

@st.cache_data(ttl=30)
def fetch_raw(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        return pd.read_csv(StringIO(res.text))
    except: return pd.DataFrame()

def process_log(df, tgl):
    log = {}; target = tgl.strftime('%d/%m/%Y')
    if not df.empty:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[df.columns[0]]).sort_values(by=df.columns[0])
        for _, r in df.iterrows():
            ts = r.iloc[0]
            if ts.strftime('%d/%m/%Y') == target:
                n = str(r.iloc[1]).strip()
                if n not in log: log[n] = {"m": ts.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if ts.hour < 9 else "LUPA ABSEN"}
                if ts.hour >= 15: log[n]["p"] = ts.strftime("%H:%M")
    return log

# 5. TAMPILAN
wita_now = get_wita()
st.markdown(f'<div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

tgl_pilihan = st.date_input("Filter Tanggal", wita_now.date(), label_visibility="collapsed")

# Fetch data Sheets
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

log_all = {**process_log(fetch_raw(URL_PNS), tgl_pilihan), **process_log(fetch_raw(URL_PPPK), tgl_pilihan)}

def render_list(log, master):
    for idx, n in enumerate(master):
        d = log.get(n, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        cl = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if "LUPA" in d["k"] else "#f87171"
        
        c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
        with c1:
            if st.button(f"👤 {n.split(',')[0]}", key=f"btn_{n}_{idx}"):
                if kirim_absen_silent(n, n in MASTER_PNS):
                    st.toast(f"✅ Berhasil Absen {n}!", icon="🚀")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                else: st.error("Gagal! Cek Form")
        with c2: st.markdown(f"<div style='text-align:center'><div class='label-k'>Pagi</div><div class='val-v'>{d['m']}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div style='text-align:center'><div class='label-k'>Sore</div><div class='val-v'>{d['p']}</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div style='text-align:center'><div class='label-k'>Ket</div><div style='color:{cl}; font-weight:900;'>{d['k']}</div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:5px 0; opacity:0.1'>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
with t1: render_list(log_all, MASTER_ALL)
with t2: render_list(log_all, MASTER_PNS)
with t3: render_list(log_all, MASTER_PPPK)
