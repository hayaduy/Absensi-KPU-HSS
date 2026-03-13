import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import time
import random
from io import StringIO
import urllib3
import urllib.parse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Absensi KPU HSS", page_icon="🚀", layout="wide")

# 2. DATABASE PEGAWAI (HASIL SCAN EXCEL & SYNC GOOGLE FORM)
DATABASE_INFO = {
    # --- PNS (17 Orang) ---
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris KPU"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum dan SDM"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi"],

    # --- PPPK (14 Orang) ---
    "Sya'bani Rona Baika": ["199202072024212044", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Apriadi Rakhman": ["198904222024211013", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "M Satria Maipadly": ["198905262024211016", "Penata Kelola Pemilihan Umum Ahli Pertama"],
    "Basuki Rahmat": ["197705222024211007", "Penata Kelola Pemilihan Umum Ahli Pertama"],
    "Sulaiman": ["198411222024211010", "Penata Kelola Pemilihan Umum Ahli Pertama"],
    "Saldoz Yedi": ["198008112025211019", "Pengelola Layanan Operasional"],
    "Mastoni Ridani": ["199106012025211018", "Pengelola Layanan Operasional"],
    "Suriadi": ["199803022025211005", "Pengelola Layanan Operasional"],
    "Ami Aspihani": ["198204042025211031", "Pengelola Layanan Operasional"],
    "Abdurrahman": ["198810122025211031", "Pengelola Layanan Operasional"],
    "Emaliani": ["198906222025212027", "Pengadministrasi Umum"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "Penata Kelola Pemilihan Umum Ahli Pertama"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "Penata Kelola Pemilihan Umum Ahli Pertama"],
    "Nadianti": ["199906062025212036", "Pengadministrasi Umum"]
}

MASTER_PNS = list(DATABASE_INFO.keys())[:17]
MASTER_PPPK = list(DATABASE_INFO.keys())[17:]

# 3. CSS MODERN
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0202 0%, #1a0505 100%); color: #ffffff; }
    .header-box { text-align: center; padding: 40px 0 20px 0; }
    .clock-text { font-size: clamp(55px, 10vw, 85px); font-weight: 900; color: #ffffff; text-shadow: 0 0 40px rgba(249, 115, 22, 0.7); line-height: 1; }
    .date-text { font-size: clamp(18px, 3vw, 24px); color: #f97316; font-weight: 500; margin-top: 5px; letter-spacing: 2px; }
    div.stButton > button {
        background: rgba(255, 255, 255, 0.03) !important; color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        font-weight: 600 !important; text-align: left !important; 
        padding-left: 20px !important; height: 64px !important; border-radius: 18px !important;
    }
    div.stButton > button:hover { background: rgba(249, 115, 22, 0.2) !important; border: 1px solid #f97316 !important; }
    .status-hadir { color: #4ade80; font-weight: 900; }
    .status-lupa { color: #fb923c; font-weight: 900; }
    .status-belum { color: #f87171; font-weight: 900; }
    .marquee-container {
        position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(15, 2, 2, 0.95); backdrop-filter: blur(15px);
        padding: 14px 0; border-top: 1px solid rgba(249, 115, 22, 0.3); z-index: 1000; overflow: hidden;
    }
    .marquee-text { display: inline-block; white-space: nowrap; animation: scroll 40s linear infinite; font-size: 15px; font-weight: 600; color: #fca5a5; }
    @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNGSI DATA
def get_wita(): return datetime.utcnow() + timedelta(hours=8)

@st.cache_data(ttl=15)
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

# 5. UI HEADER
wita_now = get_wita()
st.markdown(f"""<div class="header-box"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div><div class="date-text">{wita_now.strftime("%A, %d %B %Y").upper()}</div></div>""", unsafe_allow_html=True)
tgl_pilihan = st.date_input("Filter", wita_now.date(), label_visibility="collapsed")

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
log_all = {**process_log(fetch_raw(URL_PNS), tgl_pilihan), **process_log(fetch_raw(URL_PPPK), tgl_pilihan)}

# 6. POP-UP DENGAN URL ENCODING & JABATAN SYNC
@st.dialog("Konfirmasi Kehadiran")
def show_confirm_modal(n):
    form_id = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if n in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
    info = DATABASE_INFO.get(n)
    nama_enc = urllib.parse.quote_plus(n)
    nip_enc = urllib.parse.quote_plus(info[0])
    jab_enc = urllib.parse.quote_plus(info[1])
    url_submit = f"https://docs.google.com/forms/d/e/{form_id}/formResponse?entry.960346359={nama_enc}&entry.468881973={nip_enc}&entry.159009649={jab_enc}&submit=Submit"
    st.subheader(f"{n}")
    st.write(f"Jabatan: {info[1]}")
    st.markdown(f"""<br><a href="{url_submit}" target="_blank" style="text-decoration: none; display: block; background: linear-gradient(90deg, #f97316, #ea580c); color: white; text-align: center; padding: 18px; border-radius: 15px; font-weight: 800; font-size: 18px; box-shadow: 0 10px 25px rgba(249,115,22,0.4);">KONFIRMASI & KIRIM ✅</a>""", unsafe_allow_html=True)

# 7. RENDER LIST
def render_list(log, master_list, tab_id):
    for idx, n in enumerate(master_list):
        d = log.get(n, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        cl_class = "status-hadir" if d["k"]=="HADIR" else "status-lupa" if "LUPA" in d["k"] else "status-belum"
        c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
        with c1:
            if st.button(f"👤 {n.split(',')[0]}", key=f"btn_{tab_id}_{idx}", use_container_width=True): show_confirm_modal(n)
        with c2: st.markdown(f"<div style='text-align:center'><div class='label-k'>Pagi</div><div class='val-v'>{d['m']}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div style='text-align:center'><div class='label-k'>Sore</div><div class='val-v'>{d['p']}</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div style='text-align:center'><div class='label-k'>Ket</div><div class='{cl_class}'>{d['k']}</div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:8px 0; border:0; border-top: 1px solid rgba(255,255,255,0.05)'>", unsafe_allow_html=True)

# 8. TABS & FOOTER
st.markdown("<br>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🌎 SEMUA (31)", "👥 PNS (17)", "👥 PPPK (14)"])
with t1: render_list(log_all, list(DATABASE_INFO.keys()), "tab1")
with t2: render_list(log_all, MASTER_PNS, "tab2")
with t3: render_list(log_all, MASTER_PPPK, "tab3")

st.markdown(f"""<div class="marquee-container"><div class="marquee-text">🔴 MONITORING ABSENSI SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN --- JANGAN LUPA ABSEN PAGI DAN SORE --- TETAP SEMANGAT BEKERJA UNTUK NEGERI --- DATA TER-UPDATE SECARA OTOMATIS --- JAM WITA: {wita_now.strftime("%H:%M")} --- HARI INI: {wita_now.strftime("%d %B %Y")}</div></div><br><br><br>""", unsafe_allow_html=True)
