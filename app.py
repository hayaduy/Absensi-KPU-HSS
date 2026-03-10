import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS: MOBILE & TABLE OPTIMIZED ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 60px; color: #3498db; font-weight: bold; margin-bottom: 0px; }
    
    /* Tombol Cek Absen Gede & Tengah */
    div[data-testid="stDateInput"] { margin: 0 auto; width: 85% !important; }
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 85% !important;
        height: 60px !important;
        font-size: 22px !important;
        font-weight: bold !important;
        margin: 10px auto !important;
        display: block !important;
        border-radius: 12px !important;
    }

    /* Baris Zebra */
    [data-testid="stVerticalBlock"] > div:nth-child(even) {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 5px;
    }

    /* Tombol P & S Bulat */
    .stButton button {
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        margin: 0 auto !important;
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

# --- ZONA WAKTU ---
wita_now = datetime.now() + timedelta(hours=8)
is_pagi_time = wita_now.hour < 11

st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

tgl_pilihan = st.date_input("Pilih Tanggal", wita_now.date(), label_visibility="collapsed")
if st.button("🔍 CEK ABSEN"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        # FIX: Ubah kolom 1 ke string, lalu ke datetime secara sangat hati-hati
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0].astype(str), dayfirst=True, errors='coerce')
        return df.dropna(subset=[df.columns[0]])
    except: return pd.DataFrame()

def kirim_absen(url, nama, sesi):
    try:
        requests.post(url, data={"entry.960346359": nama}, timeout=10)
        st.toast(f"✅ BERHASIL {sesi}: {nama.split(',')[0]}!")
        time.sleep(0.5)
        st.rerun()
    except: st.error("Gagal kirim data.")

def render_list(df, master, form_url, prefix):
    t_m, t_p = datetime.strptime("09:00", "%H:%M").time(), datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        # FIX: Filter tanggal menggunakan perbandingan string YYYY-MM-DD yang jauh lebih stabil
        tgl_target_str = tgl_pilihan.strftime('%Y-%m-%d')
        # Pastikan kolom 0 adalah datetime sebelum menggunakan .dt
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
        df_day = df[df.iloc[:, 0].dt.strftime('%Y-%m-%d') == tgl_target_str]
        
        for _, r in df_day.iterrows():
            nama, jam = str(r.iloc[1]).strip(), r.iloc[0].time()
            if nama not in log:
                log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HDR" if jam <= t_m else "TLT"}
            elif jam >= t_p:
                log[nama]["p"] = jam.strftime("%H:%M")

    # Header
    st.write("---")
    h1, h2, h3, h4, h5, h6 = st.columns([0.5, 3.5, 1, 1, 1, 2.5])
    h1.write("**#**"); h2.write("**NAMA**"); h3.write("**PAGI**"); h4.write("**SORE**"); h5.write("**ST**"); h6.write("**AKSI**")
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "green" if d["k"]=="HDR" else "orange" if d["k"]=="TLT" else "red"
        
        with st.container():
            c1, c2, c3, c4, c5, c6 = st.columns([0.5, 3.5, 1, 1, 1, 2.5])
            c1.write(f"{i}")
            c2.write(f"**{p.split(',')[0]}**")
            c3.write(d["m"])
            c4.write(d["p"])
            c5.markdown(f":{clr}[**{d['k']}**]")
            
            with c6:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("P", key=f"p_{prefix}_{i}", disabled=not is_pagi_time, type="primary" if is_pagi_time else "secondary"):
                        kirim_absen(form_url, p, "PAGI")
                with b2:
                    if st.button("S", key=f"s_{prefix}_{i}", disabled=is_pagi_time, type="primary" if not is_pagi_time else "secondary"):
                        kirim_absen(form_url, p, "SORE")

tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")
