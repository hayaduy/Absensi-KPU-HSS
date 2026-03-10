import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS MAGIC: FIX VERTICAL & ZEBRA ---
st.markdown("""
    <style>
    .block-container { padding: 1rem !important; }
    
    /* Jam & Judul */
    .centered-text { text-align: center; }
    .big-clock {
        text-align: center;
        color: #3498db;
        font-weight: bold;
        font-size: calc(30px + 3vw);
        margin-bottom: 20px;
    }

    /* Paksa kolom tetap sejajar kesamping di HP (Anti-Melorot) */
    [data-testid="column"] {
        min-width: 0px !important;
        flex-basis: auto !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
    }

    /* Zebra Stripes */
    .zebra-row {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px;
        padding: 5px 0px;
    }

    /* Tombol Cek Absen Utama */
    div.stButton > button:first-child {
        width: 250px !important;
        margin: 0 auto;
        display: block;
        background-color: #d35400;
        border-radius: 10px;
    }

    /* Tombol ABSEN di Tabel */
    .small-absen-btn button {
        padding: 2px 10px !important;
        font-size: 12px !important;
        height: 30px !important;
        width: 100% !important;
    }

    @media (max-width: 600px) {
        .stMarkdown div { font-size: 11px !important; }
        .big-clock { font-size: 40px !important; }
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

# --- HEADER ---
wita_now = datetime.now() + timedelta(hours=8)
st.markdown("<h3 class='centered-text'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='big-clock'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

# --- KONTROL ---
c_l, c_m, c_r = st.columns([1, 4, 1])
with c_m:
    tgl_pilihan = st.date_input("Tgl", wita_now.date(), label_visibility="collapsed")
    if st.button("🔍 CEK ABSEN"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        for col in df.columns[:2]: df[col] = pd.to_datetime(df[col], dayfirst=True, errors='ignore')
        return df
    except: return pd.DataFrame()

def draw_rows(df, master, form_url):
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
            elif jam >= t_pulang: log[nama]["p"] = jam.strftime("%H:%M")

    st.divider()
    # Header Tabel
    h1, h2, h3, h4, h5, h6 = st.columns([0.5, 3.5, 1, 1, 1.5, 1.5])
    h1.write("**#**"); h2.write("**NAMA**"); h3.write("**M**"); h4.write("**P**"); h5.write("**ST**"); h6.write("**AKSI**")
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "p": "--:--", "k": "❌"})
        # Aplikasi Zebra Stripe pada baris genap
        row_class = "zebra-row" if i % 2 == 0 else ""
        st.markdown(f"<div class='{row_class}'>", unsafe_allow_html=True)
        
        r1, r2, r3, r4, r5, r6 = st.columns([0.5, 3.5, 1, 1, 1.5, 1.5])
        r1.write(str(i))
        r2.write(f"**{p}**")
        r3.write(d["m"])
        r4.write(d["p"])
        
        color = "green" if "HADIR" in d["k"] else "orange" if "TERLAMBAT" in d["k"] else "red"
        st_text = "HDR" if "HADIR" in d["k"] else "TLT" if "TERLAMBAT" in d["k"] else "ALPA"
        r5.markdown(f":{color}[**{st_text}**]")
        
        with r6:
            st.markdown("<div class='small-absen-btn'>", unsafe_allow_html=True)
            if st.button("ABSEN", key=f"v_{p}_{i}"):
                requests.post(form_url, data={"entry.960346359": p})
                st.toast(f"✅ {p} Sukses!")
                time.sleep(0.5); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])
with tab1: draw_rows(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: draw_rows(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)
