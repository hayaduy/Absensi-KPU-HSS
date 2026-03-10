import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS: TETAP RAPI & SEJAJAR ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 50px; color: #3498db; font-weight: bold; margin-bottom: 0px; }
    
    div.stButton > button:first-child {
        background-color: #d35400 !important; color: white !important;
        width: 85% !important; height: 55px !important; margin: 10px auto !important; 
        display: block !important; border-radius: 10px !important; font-size: 18px !important;
    }

    .stHorizontalBlock {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        border-bottom: 1px solid #444;
        padding: 10px 0;
        min-width: 650px;
    }

    .stButton button[kind="primary"], .stButton button[kind="secondary"] {
        border-radius: 6px !important;
        width: 100% !important;
        height: 50px !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    
    div[data-testid="column"] { padding: 0 2px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATA ---
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# --- ENTRY ID & FORM ENDPOINT ---
E_ID = "960346359"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

wita_now = datetime.now() + timedelta(hours=8)
is_pagi_time = wita_now.hour < 16

st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
if st.button("🔍 CEK DATA TERBARU"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        return df.dropna(subset=[df.columns[0]])
    except: return pd.DataFrame()

# MESIN SUBMIT BARU: URL REDIRECT (ANTI-BLOCK)
def trigger_submit(form_url, nama):
    import urllib.parse
    enc_nama = urllib.parse.quote(nama)
    # Link submit langsung
    final_url = f"{form_url}?entry.{E_ID}={enc_nama}&submit=Submit"
    
    # Trik: Redirect otomatis ke link submit, lalu balik lagi
    st.markdown(f'<meta http-equiv="refresh" content="0;URL=\'{final_url}\'">', unsafe_allow_html=True)
    st.write(f"Sedang memproses absen {nama.split(',')[0]}...")
    time.sleep(2)
    st.rerun()

def render_view(df, master, form_url, prefix):
    t_limit = datetime.strptime("09:00", "%H:%M").time()
    t_out = datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        t_str, t_str_alt = tgl_pilihan.strftime('%d/%m/%Y'), tgl_pilihan.strftime('%Y-%m-%d')
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if t_str in ts or t_str_alt in ts:
                try:
                    dt = pd.to_datetime(ts, dayfirst=True)
                    nama, jam = str(r.iloc[1]).strip(), dt.time()
                    if nama not in log:
                        status = "HDR" if jam <= t_limit else "TLT"
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": status}
                    elif jam >= t_out:
                        log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.write("---")
    h1, h2, h3, h4, h5, h6, h7 = st.columns([0.4, 3.4, 1.1, 1.1, 0.8, 0.9, 0.9])
    h1.write("#"); h2.write("NAMA"); h3.write("IN"); h4.write("OUT"); h5.write("ST"); h6.write("P"); h7.write("S")
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "green" if d["k"]=="HDR" else "orange" if d["k"]=="TLT" else "red"
        
        c1, c2, c3, c4, c5, c6, c7 = st.columns([0.4, 3.4, 1.1, 1.1, 0.8, 0.9, 0.9])
        c1.write(i); c2.write(f"**{p.split(',')[0]}**")
        c3.write(d["m"]); c4.write(d["p"]); c5.markdown(f":{clr}[**{d['k']}**]")
        
        with c6:
            if st.button("P", key=f"p_{prefix}_{i}", disabled=not is_pagi_time):
                trigger_submit(form_url, p)
        with c7:
            if st.button("S", key=f"s_{prefix}_{i}", disabled=is_pagi_time):
                trigger_submit(form_url, p)

tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_view(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_view(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")
