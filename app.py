import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS: TAMPILAN RAPI & TOMBOL RAPAT ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 55px; color: #3498db; font-weight: bold; margin-bottom: 0px; }
    
    /* Tombol Utama */
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 85% !important;
        height: 60px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        margin: 10px auto !important;
        display: block !important;
        border-radius: 12px !important;
    }

    /* Container Baris */
    .stHorizontalBlock {
        align-items: center !important;
        border-bottom: 1px solid #333;
        padding: 5px 0;
    }

    /* Tombol P & S Bulat & Rapat */
    .stButton button {
        border-radius: 50% !important;
        width: 42px !important;
        height: 42px !important;
        font-weight: bold !important;
        font-size: 15px !important;
        padding: 0 !important;
    }
    
    /* Menghilangkan padding antar kolom tombol agar mepet */
    div[data-testid="column"] {
        padding: 0 1px !important;
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

# --- TIME ---
wita_now = datetime.now() + timedelta(hours=8)
curr_time = wita_now.time()
is_pagi_range = curr_time < datetime.strptime("16:00", "%H:%M").time()

st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
if st.button("🔍 CEK DATA TERBARU"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.columns = df.columns.str.strip()
        return df.dropna(subset=[df.columns[0]])
    except: return pd.DataFrame()

def kirim_data_final(url, nama, tipe):
    # Menggunakan payload form-encoded yang lebih kuat
    form_data = {"entry.960346359": nama}
    try:
        # Kirim dengan simulasi browser (User-Agent) agar tidak ditolak Google
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.post(url, data=form_data, headers=headers, timeout=10)
        if response.status_code == 200:
            st.toast(f"✅ BERHASIL: {nama.split(',')[0]} ({tipe})")
            time.sleep(1)
            st.rerun()
        else:
            st.error(f"Gagal Kirim (Code: {response.status_code})")
    except:
        st.error("Koneksi bermasalah!")

def render_list(df, master, form_url, prefix):
    t_batas = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        target_str = tgl_pilihan.strftime('%d/%m/%Y')
        target_str_alt = tgl_pilihan.strftime('%Y-%m-%d')
        
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if target_str in ts or target_str_alt in ts:
                try:
                    dt_obj = pd.to_datetime(ts, dayfirst=True)
                    nama, jam = str(r.iloc[1]).strip(), dt_obj.time()
                    if nama not in log:
                        # Logika: <= 9 HDR, > 9 TLT
                        status = "HDR" if jam <= t_batas else "TLT"
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": status}
                    elif jam >= t_pulang:
                        log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.write("---")
    # Header Kolom
    h1, h2, h3, h4, h5, h6, h7 = st.columns([0.5, 3.5, 1, 1, 0.8, 0.6, 0.6])
    h1.write("**#**"); h2.write("**NAMA**"); h3.write("**PAGI**"); h4.write("**SORE**"); h5.write("**ST**"); h6.write("**P**"); h7.write("**S**")
    
    for i, p in enumerate(sorted(master), 1):
        d = log.get(p.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "green" if d["k"]=="HDR" else "orange" if d["k"]=="TLT" else "red"
        
        with st.container():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 3.5, 1, 1, 0.8, 0.6, 0.6])
            c1.write(f"{i}")
            c2.write(f"**{p.split(',')[0]}**")
            c3.write(d["m"])
            c4.write(d["p"])
            c5.markdown(f":{clr}[**{d['k']}**]")
            
            with c6:
                # Tombol Pagi aktif sampai jam 16:00
                if st.button("P", key=f"p_{prefix}_{i}", disabled=not is_pagi_range):
                    kirim_data_final(form_url, p, "PAGI")
            with c7:
                # Tombol Sore aktif dari jam 16:00 ke atas
                if st.button("S", key=f"s_{prefix}_{i}", disabled=is_pagi_range):
                    kirim_data_final(form_url, p, "SORE")

tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_list(fetch_data(URL_PNS), MASTER_DATA["PNS"], FORM_PNS, "pns")
with tab2: render_list(fetch_data(URL_PPPK), MASTER_DATA["PPPK"], FORM_PPPK, "pppk")
