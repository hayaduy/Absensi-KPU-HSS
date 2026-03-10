import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS MAGIC: RESPONSIVE DESIGN ---
st.markdown("""
    <style>
    /* Reset padding biar full di HP */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    
    /* Judul yang ukurannya menyesuaikan layar */
    .responsive-title {
        text-align: center;
        font-size: calc(18px + 1.5vw);
        font-weight: bold;
        margin-bottom: 0px;
    }

    /* Jam Digital yang ukurannya adaptif */
    .responsive-clock {
        text-align: center;
        color: #3498db;
        font-weight: bold;
        font-size: calc(35px + 3vw);
        margin-top: -10px;
        margin-bottom: 20px;
    }

    /* Membungkus Kontrol (Tanggal & Tombol) agar rapi di semua layar */
    .control-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
    }

    /* Tombol yang proporsional */
    div.stButton > button {
        width: 100% !important;
        height: 55px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }

    /* Meratakan Tabs ke tengah */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; }
    .stTabs [data-baseweb="tab"] { font-size: calc(14px + 0.5vw) !important; }

    /* Pengaturan Tabel Monitoring */
    .monitor-row {
        padding: 10px;
        border-bottom: 1px solid #444;
        display: flex;
        align-items: center;
    }
    
    /* Sembunyikan elemen tertentu kalau di HP biar gak sumpek */
    @media (max-width: 600px) {
        .stMarkdown div { font-size: 13px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA MASTER ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

# --- HEADER & JAM ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown("<div class='responsive-title'>📊 MONITORING ABSENSI KPU HSS</div>", unsafe_allow_html=True)
st.markdown(f"<div class='responsive-clock'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# --- KONTROL UTAMA ---
# Menggunakan columns dengan perbandingan yang aman untuk HP (1:4:1)
c_gap1, c_main, c_gap2 = st.columns([1, 6, 1])
with c_main:
    tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
    if st.button("🔍 CEK ABSEN"):
        st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        for col in df.columns[:2]:
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='ignore')
        return df
    except: return pd.DataFrame()

def draw_table(df, master, form_url):
    t_limit = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        df_clean = df.copy()
        time_col, name_col = df_clean.columns[0], df_clean.columns[1]
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], errors='coerce')
        df_clean = df_clean.dropna(subset=[time_col])
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        
        for _, r in df_day.iterrows():
            nama, jam = str(r[name_col]).strip(), r[time_col].time()
            if nama not in log:
                log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}
            elif jam >= t_pulang:
                log[nama]["p"] = jam.strftime("%H:%M")

    st.divider()
    # Penyesuaian lebar kolom: Nama dapat porsi paling besar
    c1, c2, c3, c4, c5, c6 = st.columns([0.6, 4, 1.2, 1.2, 2, 1.2])
    c1.write("**#**"); c2.write("**NAMA**"); c3.write("**M**"); c4.write("**P**"); c5.write("**STAT**"); c6.write("**AKSI**")
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "❌ ALPA"})
        r1, r2, r3, r4, r5, r6 = st.columns([0.6, 4, 1.2, 1.2, 2, 1.2])
        r1.write(str(i))
        r2.write(f"**{p}**")
        r3.write(d["m"])
        r4.write(d["p"])
        color = "green" if "HADIR" in d["k"] else "orange" if "TERLAMBAT" in d["k"] else "red"
        r5.markdown(f":{color}[{d['k']}]")
        if r6.button("✔", key=f"btn_{p}_{i}"):
            requests.post(form_url, data={"entry.960346359": p})
            st.toast(f"✅ {p} Sukses!")
            time.sleep(0.5); st.rerun()

# --- TABS ---
tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])
with tab1: draw_table(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: draw_table(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
