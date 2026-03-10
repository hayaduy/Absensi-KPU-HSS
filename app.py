import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS: MOBILE OPTIMIZED ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 65px; color: #3498db; font-weight: bold; margin-bottom: 5px; }
    
    /* Center & Big Controls */
    div[data-testid="stDateInput"] { margin: 0 auto; width: 90% !important; }
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 90% !important;
        height: 70px !important;
        font-size: 26px !important;
        font-weight: bold !important;
        margin: 10px auto !important;
        display: block !important;
        border-radius: 15px !important;
    }

    /* Zebra & Row Styling */
    div[data-testid="stVerticalBlock"] > div:nth-child(even) {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }

    /* Tombol P & S Bulat Gede */
    .stButton button {
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        font-weight: bold !important;
        font-size: 20px !important;
        margin: 0 auto !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATA ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

# --- TIME ---
now_wita = datetime.now() + timedelta(hours=8)
current_hour = now_wita.hour
is_pagi = current_hour < 11

st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{now_wita.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

tgl_pilihan = st.date_input("Tanggal", now_wita.date(), label_visibility="collapsed")
if st.button("🔍 CEK ABSEN"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        return df
    except: return pd.DataFrame()

def kirim_ke_gform(url, nama, tipe):
    # ID Entry untuk Nama (entry.960346359)
    payload = {"entry.960346359": nama}
    try:
        requests.post(url, data=payload, timeout=10)
        st.success(f"BERHASIL! Absen {tipe} untuk {nama.split(',')[0]} terkirim.")
        time.sleep(1)
        st.rerun()
    except:
        st.error("Waduh, gagal kirim! Cek internet Abang.")

def render_list(df, master, form_url, prefix):
    t_m, t_s = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    if not df.empty:
        df_clean = df.copy()
        time_col, name_col = df_clean.columns[0], df_clean.columns[1]
        df_day = df_clean[df_clean[time_col].dt.date == tgl_pilihan]
        for _, r in df_day.iterrows():
            nama, jam = str(r[name_col]).strip(), r[time_col].time()
            if nama not in log: log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HDR" if jam <= t_m else "TLT"}
            elif jam >= t_s: log[nama]["p"] = jam.strftime("%H:%M")

    # Header Manual biar lurus
    st.write("---")
    h1, h2, h3, h4, h5, h6 = st.columns([0.5, 3, 1, 1, 1, 2.5])
    h1.write("**#**"); h2.write("**NAMA**"); h3.write("**PAGI**"); h4.write("**SORE**"); h5.write("**ST**"); h6.write("**ABSEN**")
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "green" if d["k"]=="HDR" else "orange" if d["k"]=="TLT" else "red"
        
        # Row Container
        with st.container():
            c1, c2, c3, c4, c5, c6 = st.columns([0.5, 3, 1, 1, 1, 2.5])
            c1.write(f"{i}")
            c2.write(f"**{p.split(',')[0]}**")
            c3.write(f"{d['m']}")
            c4.write(f"{d['p']}")
            c5.markdown(f":{clr}[**{d['k']}**]")
            
            # Tombol P dan S sejajar
            with c6:
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("P", key=f"p_{prefix}_{i}", disabled=not is_pagi, type="primary" if is_pagi else "secondary"):
                        kirim_ke_gform(form_url, p, "PAGI")
                with btn_col2:
                    if st.button("S", key=f"s_{prefix}_{i}", disabled=is_pagi, type="primary" if not is_pagi else "secondary"):
                        kirim_ke_gform(form_url, p, "SORE")

tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])
with tab1: render_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")
