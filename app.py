import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# CSS Custom untuk merapikan posisi ke tengah dan memperbesar elemen
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 50px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 24px !important;
        font-weight: bold !important;
    }
    div[data-testid="stDateInput"] {
        width: 300px !important;
        margin: 0 auto !important;
    }
    div[data-testid="stButton"] button {
        display: block;
        margin: 0 auto;
        width: 400px !important;
        height: 80px !important;
        font-size: 30px !important;
        font-weight: bold !important;
        border-radius: 15px;
    }
    h1, h2, h3 {
        text-align: center !important;
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
st.markdown("<h1>📊 MONITORING ABSENSI KPU HSS</h1>", unsafe_allow_html=True)
st.markdown(f"<h1 style='color: #3498db; font-size: 60px; margin-bottom: 0px;'>{wita_now.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)

# --- PILIH TANGGAL (Center) ---
st.markdown("<br>", unsafe_allow_html=True)
tgl_pilihan = st.date_input("📅 Pilih Tanggal Scan/Absen", wita_now.date(), label_visibility="collapsed")

# --- TOMBOL CEK ABSEN (Center & Big) ---
st.markdown("<br>", unsafe_allow_html=True)
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
        time_col = df_clean.columns[0]
        name_col = df_clean.columns[1]
        df_clean[time_col] = pd.to_datetime(df_clean[time_col], errors='coerce')
        df_clean = df_clean.dropna(subset=[time_col])
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        
        for _, r in df_day.iterrows():
            nama = str(r[name_col]).strip()
            jam = r[time_col].time()
            if nama not in log:
                log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}
            elif jam >= t_pulang:
                log[nama]["p"] = jam.strftime("%H:%M")

    # Layout Tabel Monitoring
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns([0.5, 3, 1, 1, 1.5, 1])
    c1.write("**NO**"); c2.write("**NAMA PEGAWAI**"); c3.write("**MASUK**"); c4.write("**PULANG**"); c5.write("**STATUS**"); c6.write("**AKSI**")
    st.divider()

    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "❌ ALPA"})
        r1, r2, r3, r4, r5, r6 = st.columns([0.5, 3, 1, 1, 1.5, 1])
        r1.write(str(i)); r2.write(f"**{p}**"); r3.write(d["m"]); r4.write(d["p"])
        color = "green" if "HADIR" in d["k"] else "orange" if "TERLAMBAT" in d["k"] else "red"
        r5.markdown(f":{color}[{d['k']}]")
        if r6.button("ABSEN", key=f"btn_{p}_{i}"):
            requests.post(form_url, data={"entry.960346359": p})
            st.toast(f"✅ Absen {p} Sukses!"); time.sleep(1); st.rerun()

# --- TABS (Center & Big) ---
st.markdown("<br>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: draw_ui(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: draw_ui(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
