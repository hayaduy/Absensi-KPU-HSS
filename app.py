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

# 2. CSS CUSTOM
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
    .block-container { padding-top: 2rem; max-width: 1000px !important; margin: 0 auto; }
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { 
        font-size: clamp(45px, 12vw, 90px); 
        font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 25px rgba(249, 115, 22, 0.6); 
        font-family: 'Courier New', Courier, monospace;
    }
    .running-text-container { width: 100%; overflow: hidden; margin-bottom: 30px; background: rgba(0,0,0,0.3); padding: 12px 0; border-radius: 12px; }
    .running-text { font-size: 15px; font-weight: 600; color: #ffffff; white-space: nowrap; animation: scroll-left 30s linear infinite; display: inline-block; }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    div.stButton > button {
        background-color: rgba(249, 115, 22, 0.15) !important;
        color: #fecaca !important;
        border: 1px solid rgba(249, 115, 22, 0.4) !important;
        font-weight: bold !important;
        text-align: left !important;
        padding-left: 20px !important;
        height: 60px !important;
        border-radius: 15px !important;
    }
    div.stButton > button:hover {
        background-color: rgba(249, 115, 22, 0.4) !important;
        border: 1px solid #f97316 !important;
        color: white !important;
    }
    .label-k { font-size: 11px; color: #fca5a5; text-transform: uppercase; }
    .val-v { font-size: 19px; font-weight: 800; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 3. DATABASE NIP & JABATAN (PENTING!)
# Kita butuh ini supaya pas klik Nama, sistem tau NIP & Jabatannya otomatis
DATABASE_PEGAWAI = {
    # FORMAT: "Nama Lengkap": ["NIP", "JABATAN"]
    "Suwanto, SH., MH.": ["197103031993031005", "SEKRETARIS"],
    "Wawan Setiawan, SH": ["198105252009041001", "KASUBBAG TEKNIS"],
    "Ineke Setiyaningsih, S.Sos": ["197505242006042017", "KASUBBAG KEUANGAN"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN OPERASIONAL"],
    # Tambahkan pegawai lainnya di sini sesuai format di atas
}

def get_wita_now():
    return datetime.utcnow() + timedelta(hours=8)

# URL DATA (Sheets)
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# FORM LINKS
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

# 4. FUNGSI KIRIM (MULTIPLE DATA)
def kirim_absen_silent(nama, is_pns):
    target = FORM_PNS if is_pns else FORM_PPPK
    
    # Ambil NIP & Jabatan dari database kita di atas
    info = DATABASE_PEGAWAI.get(nama, ["-", "STAF"])
    
    payload = {
        "entry.960346359": nama,
        "entry.468881973": info[0],
        "entry.159009649": info[1]
    }
    
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post(target, data=payload, headers=headers, timeout=15)
        return r.status_code == 200
    except: return False

# --- PROSES DATA SEPERTI BIASA ---
@st.cache_data(ttl=30)
def fetch_raw(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        return pd.read_csv(StringIO(res.text))
    except: return pd.DataFrame()

def process_log(df, tgl_target):
    log = {}
    target_str = tgl_target.strftime('%d/%m/%Y')
    if not df.empty:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[df.columns[0]]).sort_values(by=df.columns[0])
        for _, r in df.iterrows():
            ts = r.iloc[0]
            if ts.strftime('%d/%m/%Y') == target_str:
                nama = str(r.iloc[1]).strip()
                if nama not in log:
                    log[nama] = {"m": ts.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if ts.hour < 9 else "LUPA ABSEN"}
                if ts.hour >= 15: log[nama]["p"] = ts.strftime("%H:%M")
    return log

def render_list(log, master, tgl_pilihan, wita_now):
    for idx, n in enumerate(master):
        nama = n.strip()
        d = log.get(nama, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        
        # Logika Keterangan
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
            elif wita_now.hour >= 16: d["k"] = "LAPOR"
            elif wita_now.hour >= 9: d["k"] = "LUPA"
        
        cl = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if "LAPOR" in d["k"] or "LUPA" in d["k"] else "#f87171"
        
        c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
        with c1:
            if st.button(f"👤 {nama.split(',')[0]}", key=f"btn_{idx}_{nama}"):
                if kirim_absen_silent(nama, nama in MASTER_PNS):
                    st.toast(f"✅ Berhasil Absen {nama}!", icon="🚀")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
                else: st.error("Gagal! Cek Jaringan.")
        with c2: st.markdown(f"<div style='text-align:center'><div class='label-k'>Pagi</div><div class='val-v'>{d['m']}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div style='text-align:center'><div class='label-k'>Sore</div><div class='val-v'>{d['p']}</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div style='text-align:center'><div class='label-k'>Ket</div><div style='color:{cl}; font-weight:900;'>{d['k']}</div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:5px 0; opacity:0.1'>", unsafe_allow_html=True)

# 6. FLOW UTAMA
wita_now = get_wita_now()
st.markdown(f'<div class="header-jam"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

tgl_pilihan = st.date_input("Filter", wita_now.date(), label_visibility="collapsed")

MASTER_PNS = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos"] # Sederhanakan list buat tes
MASTER_PPPK = ["Abdurrahman"] 

log_all = {**process_log(fetch_raw(URL_PNS), tgl_pilihan), **process_log(fetch_raw(URL_PPPK), tgl_pilihan)}

t1, t2 = st.tabs(["🌎 SEMUA", "👥 PNS"])
with t1: render_list(log_all, MASTER_PNS + MASTER_PPPK, tgl_pilihan, wita_now)
