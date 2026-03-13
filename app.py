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

# 2. DATABASE PEGAWAI (PRESISI 100% SESUAI EXCEL)
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kepala Sub. Bagian Teknis Pemilu, Partisipasi dan Hubungan Masyarakat"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kepala Sub Bagian Keuangan, Umum dan Logistik"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kepala Sub. Bagian Hukum dan Sumber Daya Manusia"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kepala Sub. Bagian Perencanaan Data dan Informasi"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem dan Teknologi Informasi"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem dan Teknologi Informasi"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem dan Teknologi Informasi"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola layanan operasional"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum dan Perundang-Undangan"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum dan Perundang-Undangan"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem dan Teknologi Informasi"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem dan Teknologi Informasi"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem dan Teknologi Informasi"],
    "Sya'bani Rona Baika": ["199202072024212044", "Ahli Pertama-Pranata Komputer"],
    "Apriadi Rakhman": ["198904222024211013", "Ahli Pertama-Pranata Komputer"],
    "M Satria Maipadly": ["198905262024211016", "Ahli Pertama-Penata Kelola Pemilu"],
    "Basuki Rahmat": ["197705222024211007", "Penata Kelola Pemilihan Umum Ahli Pertama"],
    "Sulaiman": ["198411222024211010", "Penata Kelola Pemilihan Umum Ahli Pertama"],
    "Saldoz Yedi": ["198008112025211019", "Operator Layanan Operasional"],
    "Mastoni Ridani": ["199106012025211018", "Operator Layanan Operasional"],
    "Suriadi": ["199803022025211005", "Pengelola Umum Operasional"],
    "Ami Aspihani": ["198204042025211031", "Operator Layanan Operasional"],
    "Abdurrahman": ["198810122025211031", "Operator Layanan Operasional"],
    "Emaliani": ["198906222025212027", "Pengadministrasi Perkantoran"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN"]
}

MASTER_PNS = list(DATABASE_INFO.keys())[:17]
MASTER_PPPK = list(DATABASE_INFO.keys())[17:]

# 3. CSS MODERN
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
    .clock-text { font-size: clamp(40px, 8vw, 70px); font-weight: 900; text-align: center; color: white; text-shadow: 0 0 20px #f97316; margin-bottom: 20px; }
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
    info = DATABASE_INFO.get(nama)
    
    # Payload Lengkap (Nama, NIP, Jabatan) + Parameter Anti-Draft
    payload = {
        "entry.960346359": nama,
        "entry.468881973": info[0],
        "entry.159009649": info[1],
        "draftResponse": [],
        "pageHistory": 0
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post(target, data=payload, headers=headers, timeout=15)
        return r.status_code == 200
    except:
        return False

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

# 5. TAMPILAN UTAMA
wita_now = get_wita()
st.markdown(f'<div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

tgl_pilihan = st.date_input("Filter", wita_now.date(), label_visibility="collapsed")

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

log_all = {**process_log(fetch_raw(URL_PNS), tgl_pilihan), **process_log(fetch_raw(URL_PPPK), tgl_pilihan)}

def render_list(log, master_list):
    for idx, n in enumerate(master_list):
        d = log.get(n, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        cl = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if "LUPA" in d["k"] else "#f87171"
        c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
        with c1:
            nama_singkat = n.split(',')[0]
            if st.button(f"👤 {nama_singkat}", key=f"btn_{idx}_{n}", use_container_width=True):
                with st.spinner('Proses...'):
                    if kirim_absen_silent(n, n in MASTER_PNS):
                        st.toast(f"✅ Sukses: {nama_singkat}", icon="🚀")
                        st.cache_data.clear()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Gagal! Matikan 'Autosave' di Form.")
        with c2: st.markdown(f"<div style='text-align:center'><div class='label-k'>Pagi</div><div class='val-v'>{d['m']}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div style='text-align:center'><div class='label-k'>Sore</div><div class='val-v'>{d['p']}</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div style='text-align:center'><div class='label-k'>Ket</div><div style='color:{cl}; font-weight:900;'>{d['k']}</div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:5px 0; opacity:0.1'>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🌎 SEMUA", "👥 PNS", "👥 PPPK"])
with t1: render_list(log_all, list(DATABASE_INFO.keys()))
with t2: render_list(log_all, MASTER_PNS)
with t3: render_list(log_all, MASTER_PPPK)
