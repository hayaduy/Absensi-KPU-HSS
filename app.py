import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS SEDERHANA TAPI AMPUH ---
st.markdown("""
    <style>
    /* Meratakan judul dan jam ke tengah */
    .stApp h1, .stApp h2, .stApp h3 { text-align: center !important; }
    
    /* Tombol Cek Absen di Tengah */
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 200px !important;
        height: 50px !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Mengatur jarak tabel agar tidak rapat ke samping di Laptop */
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* Membuat baris zebra secara manual di Streamlit */
    div[data-testid="stVerticalBlock"] > div:nth-child(even) {
        background-color: rgba(255, 255, 255, 0.03);
        border-radius: 5px;
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
st.write(f"### 📊 MONITORING ABSENSI KPU HSS")
st.markdown(f"<h1 style='text-align: center; color: #3498db;'>{wita_now.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

# --- KONTROL ---
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
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

def draw_ui(df, master, form_url):
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
    # Header Kolom dengan proporsi baru agar Nama lebih lebar dan Jam tidak melorot
    h1, h2, h3, h4, h5 = st.columns([0.4, 4, 1.2, 1.2, 2])
    h1.write("**#**"); h2.write("**NAMA**"); h3.write("**M**"); h4.write("**P**"); h5.write("**STAT**")
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "❌"})
        
        # Container baris
        with st.container():
            r1, r2, r3, r4, r5 = st.columns([0.4, 4, 1.2, 1.2, 2])
            r1.write(str(i))
            r2.write(f"**{p}**")
            r3.write(d["m"])
            r4.write(d["p"])
            color = "green" if "HADIR" in d["k"] else "orange" if "TERLAMBAT" in d["k"] else "red"
            st_label = "HDR" if "HADIR" in d["k"] else "TLT" if "TERLAMBAT" in d["k"] else "ALPA"
            r5.markdown(f":{color}[**{st_label}**]")

    # Bagian Tombol Absen dibuat terpisah agar tidak merusak tabel
    st.write("---")
    st.write("**Daftar Pegawai (Klik untuk Absen):**")
    cols = st.columns(2)
    for i, p in enumerate(sorted(master)):
        with cols[i % 2]:
            nama_tombol = p.split(',')[0] # Nama panggilan saja biar muat di HP
            if st.button(f"Absen: {nama_tombol}", key=f"btn_{p}_{i}", use_container_width=True):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ {p} Sukses!")
                time.sleep(0.5)
                st.rerun()

tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])
with tab1: draw_ui(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: draw_ui(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
