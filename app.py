import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import random
from io import StringIO

# 1. Konfigurasi Dasar
st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# 2. CSS: Warna Mencolok & Layout Stabil
st.markdown("""
    <style>
    .stApp { background-color: #1a0505; color: #ffffff; }
    
    /* Jam & Header */
    .clock-container { text-align: center; padding: 10px; background: #450a0a; border-radius: 15px; margin-bottom: 20px; border: 2px solid #ea580c; }
    .clock-text { font-size: 50px; font-weight: bold; color: #fb923c; }

    /* Baris Pegawai */
    .row-absensi {
        display: flex;
        align-items: center;
        background: linear-gradient(90deg, #7f1d1d 0%, #450a0a 100%);
        margin-bottom: 8px;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #b91c1c;
        transition: 0.3s;
    }
    .row-absensi:hover { border-color: #fb923c; background: #631717; }

    /* Nama sebagai Link Mencolok */
    .link-nama {
        flex: 2;
        font-size: 20px;
        font-weight: 800;
        color: #ffffff;
        text-decoration: none;
    }
    .link-nama:hover { color: #fb923c; text-decoration: underline; }

    /* Kolom Data */
    .data-box { flex: 3; display: flex; justify-content: space-around; border-left: 2px solid #b91c1c; }
    .item { text-align: center; }
    .lbl { font-size: 10px; color: #fca5a5; text-transform: uppercase; }
    .val { font-size: 18px; font-weight: bold; }
    
    /* Status Warna */
    .status-hadir { color: #4ade80; }
    .status-telat { color: #facc15; }
    .status-alpa { color: #f87171; }
    </style>
    """, unsafe_allow_html=True)

# 3. Data & Config
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# 4. Fungsi Ambil Data
def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=5)
        return pd.read_csv(StringIO(res.text))
    except: return pd.DataFrame()

# 5. Header Jam & Auto Refresh
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="clock-container"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# Tombol Refresh Manual
if st.button("🔄 REFRESH DATA"): st.rerun()

def render_simple_list(df, master, form_url):
    t_limit = datetime.strptime("09:00", "%H:%M").time()
    log = {}
    today = wita_now.strftime('%d/%m/%Y')

    if not df.empty:
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if today in ts:
                nama, jam = str(r.iloc[1]).strip(), pd.to_datetime(ts).time()
                log[nama] = {"m": jam.strftime("%H:%M"), "k": "HADIR" if jam <= t_limit else "TERLAMBAT"}

    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--:--", "k": "ALPA"})
        cls = "status-hadir" if d['k']=="HADIR" else "status-telat" if d['k']=="TERLAMBAT" else "status-alpa"
        
        # Buat Link Form
        link = f"{form_url}?entry.{E_ID}={p.replace(' ', '+')}&submit=Submit"
        
        st.markdown(f"""
            <div class="row-absensi">
                <a href="{link}" target="_blank" class="link-nama">{i}. {p.split(',')[0]}</a>
                <div class="data-box">
                    <div class="item"><div class="lbl">Masuk</div><div class="val">{d['m']}</div></div>
                    <div class="item"><div class="lbl">Status</div><div class="val {cls}">{d['k']}</div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# 6. Tampilan Utama
tab1, tab2 = st.tabs(["PEGAWAI PNS", "PEGAWAI PPPK"])
with tab1: render_simple_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS)
with tab2: render_simple_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK)

# Auto Refresh setiap 30 detik
st.empty()
import time
time.sleep(30)
st.rerun()
