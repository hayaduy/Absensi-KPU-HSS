import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO
import urllib3

# Menghilangkan peringatan SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Monitoring Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS: STYLE MODERN & TRUE CENTER
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
    .block-container { padding-top: 1rem; max-width: 1000px !important; margin: 0 auto; }
    .header-jam { text-align: center; padding: 10px 0; }
    .clock-text { 
        font-size: clamp(40px, 10vw, 80px); 
        font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 20px rgba(249, 115, 22, 0.5); 
        font-family: 'Courier New', Courier, monospace;
    }
    .running-text-container { width: 100%; overflow: hidden; margin-bottom: 20px; background: rgba(0,0,0,0.2); padding: 10px 0; border-radius: 10px; }
    .running-text { font-size: 14px; font-weight: 600; color: #ffffff; white-space: nowrap; animation: scroll-left 30s linear infinite; display: inline-block; }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    div.stButton > button {
        background-color: rgba(249, 115, 22, 0.1) !important;
        color: #fecaca !important;
        border: 1px solid rgba(249, 115, 22, 0.3) !important;
        font-weight: bold !important;
        text-align: left !important;
        padding-left: 20px !important;
        height: 50px !important;
    }
    div.stButton > button:hover {
        background-color: rgba(249, 115, 22, 0.3) !important;
        border: 1px solid #f97316 !important;
        color: white !important;
    }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; }
    .val-v { font-size: 18px; font-weight: 800; color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# 3. KONFIGURASI DATA & WAKTU (WITA)
def get_wita_now():
    # Memastikan waktu selalu WITA (UTC+8) tidak peduli settingan jam PC
    return datetime.utcnow() + timedelta(hours=8)

PIMPINAN = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE"]
MASTER_PNS = ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."]
MASTER_PPPK = ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
MASTER_ALL = MASTER_PNS + MASTER_PPPK

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
ENTRY_ID = "960346359"

# 4. ENGINE KIRIM (DENGAN PENYAMARAN)
def kirim_absen_silent(nama, is_pns):
    target = FORM_PNS if is_pns else FORM_PPPK
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {f"entry.{ENTRY_ID}": nama}
    try:
        r = requests.post(target, data=payload, headers=headers, timeout=10, verify=False)
        return r.status_code == 200
    except: return False

def fetch_raw(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10, verify=False)
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

# 5. RENDERER
def render_list(log, master, tgl_pilihan, wita_now, is_all=False):
    items = []
    for idx, p in enumerate(master):
        nama = p.strip()
        d = log.get(nama, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        # Logika Keterangan
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < wita_now.date(): d["k"] = "ALPA"
            elif wita_now.hour >= 16: d["k"] = "LAPOR SEKRETARIS" if nama in PIMPINAN else "LAPOR KASUBBAG"
            elif wita_now.hour >= 9: d["k"] = "LUPA ABSEN"
        items.append({"n": nama, "d": d, "h": idx})

    if is_all: items = sorted(items, key=lambda x: (x['d']['m'] != "--:--", x['h']))

    for it in items:
        n = it["n"]; d = it["d"]
        cl = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"] in ["LUPA ABSEN", "LAPOR KASUBBAG", "LAPOR SEKRETARIS"] else "#f87171"
        
        c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
        with c1:
            # Tombol Aktif jika tanggal dipilih = hari ini (WITA)
            is_today = tgl_pilihan == wita_now.date()
            if st.button(f"👤 {n.split(',')[0]}", key=f"btn_{n}_{it['h']}", use_container_width=True, disabled=not is_today):
                if kirim_absen_silent(n, n in MASTER_PNS):
                    st.toast(f"✅ Sukses Absen {n.split(',')[0]}!", icon="🚀")
                    time.sleep(1)
                    st.rerun()
                else: st.error("Gagal koneksi! Pakai Hotspot HP.")

        with c2: st.markdown(f"<div style='text-align:center'><div class='label-k'>Pagi</div><div class='val-v'>{d['m']}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div style='text-align:center'><div class='label-k'>Sore</div><div class='val-v'>{d['p']}</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div style='text-align:center'><div class='label-k'>Ket</div><div style='color:{cl}; font-weight:900; font-size:13px;'>{d['k']}</div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:5px 0; opacity:0.1'>", unsafe_allow_html=True)

# 6. FLOW UTAMA
wita_now = get_wita_now()

st.markdown(f"""
    <div class="header-jam">
        <div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div>
        <div class="running-text-container">
            <div class="running-text">
                KPU HSS MONITORING • <span style="color:#facc15">KLIK NAMA UNTUK ABSEN</span> • WITA: {wita_now.strftime("%d/%m/%Y")}
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

col_l, col_m, col_r = st.columns([1, 1.2, 1])
with col_m:
    tgl_pilihan = st.date_input("Filter Tanggal", wita_now.date())

log_pns = process_log(fetch_raw(URL_PNS), tgl_pilihan)
log_pppk = process_log(fetch_raw(URL_PPPK), tgl_pilihan)
log_all = {**log_pns, **log_pppk}

t_a, t_p, t_k = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
with t_a: render_list(log_all, MASTER_ALL, tgl_pilihan, wita_now, is_all=True)
with t_p: render_list(log_pns, MASTER_PNS, tgl_pilihan, wita_now)
with t_k: render_list(log_pppk, MASTER_PPPK, tgl_pilihan, wita_now)

# 7. REFRESH AMAN
if 'last_ref' not in st.session_state: st.session_state.last_ref = time.time()
if time.time() - st.session_state.last_ref > 60:
    st.session_state.last_ref = time.time()
    st.rerun()
