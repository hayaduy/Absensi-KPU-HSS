import streamlit as st
import pandas as pd
import requests
import re
from datetime import datetime, timedelta
import time
import random
from io import StringIO
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Absensi KPU HSS", page_icon="👻", layout="wide")

# 2. DATABASE PEGAWAI (PRESISI SESUAI FOTO EXCEL)
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

# 3. STYLE CSS (DARK & MODERN)
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
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

# 4. FUNGSI CORE (GHOST BYPASS ENGINE)
def get_wita():
    return datetime.utcnow() + timedelta(hours=8)

def kirim_absen_silent(nama, is_pns):
    view_url = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/viewform" if is_pns else "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/viewform"
    post_url = view_url.replace("/viewform", "/formResponse")
    info = DATABASE_INFO.get(nama)
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0"}

    try:
        with requests.Session() as s:
            # Ambil Token FBZX dinamis
            res = s.get(view_url, headers=headers, timeout=10)
            token = re.search(r'name="fbzx" value="([^"]+)"', res.text)
            fbzx = token.group(1) if token else ""

            # Payload lengkap 3 kolom + bypass parameters
            payload = {
                "entry.960346359": nama,
                "entry.468881973": info[0],
                "entry.159009649": info[1],
                "fvv": "1",
                "pageHistory": "0",
                "fbzx": fbzx,
                "draftResponse": "[]",
                "continue": "1"
            }
            r = s.post(post_url, data=payload, headers=headers, timeout=15)
            # Sukses jika 200 atau halaman konfirmasi muncul
            return r.status_code == 200 or "recorded" in r.text.lower()
    except:
        return False

# --- PROSES DATA ---
@st.cache_data(ttl=30)
def fetch_
