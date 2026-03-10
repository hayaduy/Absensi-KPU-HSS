import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS: ANTI-ANCRIT (HP & PC SAFE) ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: calc(30px + 3vw); color: #3498db; font-weight: bold; margin-bottom: 10px; }
    
    /* Input Tanggal & Tombol Cek */
    div[data-testid="stDateInput"] { margin: 0 auto; width: 80% !important; }
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 80% !important;
        height: 60px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        margin: 10px auto !important;
        display: block !important;
        border-radius: 12px !important;
    }

    /* Tabel Monitoring: Kunci Layout agar tidak melorot di HP Vertikal */
    .stHorizontalBlock {
        align-items: center !important;
        border-bottom: 1px solid #444;
        padding: 10px 0;
        display: flex !important;
        flex-wrap: nowrap !important; /* Paksa satu baris */
    }

    /* Tombol P & S Kotak Mantap */
    .stButton button[kind="primary"], .stButton button[kind="secondary"] {
        border-radius: 8px !important;
        width: 100% !important;
        height: 45px !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 0 !important;
    }

    /* Sembunyikan Iframe (Mesin Absen Belakang Layar) */
    .hidden-iframe { display: none; }
    
    @media (max-width: 600px) {
        .stMarkdown div { font-size: 10px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA MASTER (NIP & NAMA SESUAI FOTO) ---
MASTER_DATA = {
    "PNS": {
        "Suwanto, SH., MH.": "19720521 200912 1 001",
        "Wawan Setiawan, SH": "19860601 201012 1 004",
        "Ineke Setiyaningsih, S.Sos": "19831003 200912 2 001",
        "Farah Agustina Setiawati, SH": "19840828 201012 2 003",
        "Rusma Ariati, SE": "19840621 201101 2 013",
        "Helmalina": "19680318 199003 2 003",
        "Ahmad Erwan Rifani, S.HI": "19830829 200811 1 001",
        "Syaiful Anwar": "19741127 200710 1 001",
        "Zainal Hilmi Yustan": "19821025 200701 1 003",
        "Najmi Hidayati": "19850608 200701 2 003",
        "Jainal Abidin": "19820712 200910 1 001",
        "Suci Lestari, S.Ikom": "19850108 201012 2 006",
        "Athaya Insyira Khairani, S.H": "20010712202506 2 017",
        "Muhammad Ibnu Fahmi, S.H.": "20010608202506 1 007",
        "Alfian Ridhani, S.Kom": "19950903202506 1 005",
        "Muhammad Aldi Hudaifi, S.Kom": "20010121202506 1 007",
        "Firda Aulia, S.Kom.": "20020415202506 2 007"
    },
    "PPPK": {
        "Sya'bani Rona Baika": "199202072024212044",
        "Apriadi Rakhman": "198904222024211013",
        "M Satria Maipadly": "198905262024211016",
        "Basuki Rahmat": "197705022024211007",
        "Sulaiman": "198411222024211010",
        "Saldoz Yedi": "198008112025211019",
        "Mastoni Ridani": "199106012025211018",
        "Suriadi": "199803022025211005",
        "Ami Aspihani": "198204042025211031",
        "Abdurrahman": "198810122025211031",
        "Emaliani": "198906222025212027",
        "Muhammad Hafiz Rijani, S.KOM": "199603212025211031",
        "Saiful Fahmi, S.Pd": "199506172025211036",
        "Nadianti": "199906062025212036"
    }
}

URL_CSV_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_CSV_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_URL_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_URL_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

# --- LOGIKA WAKTU ---
wita_now = datetime.now() + timedelta(hours=8)
is_pagi_range = wita_now.hour < 16

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

# MESIN ABSEN BELAKANG LAYAR (Iframe Magic)
def absen_langsung(form_url, nama):
    import urllib.parse
    encoded_nama = urllib.parse.quote(nama)
    # Trik: Kirim lewat link tapi targetnya iframe tersembunyi
    full_url = f"{form_url}?entry.960346359={encoded_nama}&submit=Submit"
    st.markdown(f'<iframe class="hidden-iframe" src="{full_url}"></iframe>', unsafe_allow_html=True)
    st.toast(f"✅ Berhasil Mengirim Absen: {nama.split(',')[0]}")
    time.sleep(1.5)
    st.rerun()

def render_list(df, master, form_url, prefix):
    t_batas = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("16:00", "%H:%M").time()
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
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": "HDR" if jam <= t_batas else "TLT"}
                    elif jam >= t_pulang: log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.write("---")
    # Header Kolom
    h1, h2, h3, h4, h5, h6, h7 = st.columns([0.5, 3.5, 1.1, 1.1, 0.8, 1, 1])
    h1.write("**#**"); h2.write("**NAMA**"); h3.write("**PAGI**"); h4.write("**SORE**"); h5.write("**ST**"); h6.write("**P**"); h7.write("**S**")
    
    for i, (nama, nip) in enumerate(master.items(), 1):
        d = log.get(nama.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "green" if d["k"]=="HDR" else "orange" if d["k"]=="TLT" else "red"
        
        c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 3.5, 1.1, 1.1, 0.8, 1, 1])
        c1.write(f"{i}")
        c2.write(f"**{nama.split(',')[0]}**")
        c3.write(d["m"])
        c4.write(d["p"])
        c5.markdown(f":{clr}[**{d['k']}**]")
        
        with c6:
            if st.button("P", key=f"p_{prefix}_{i}", disabled=not is_pagi_range):
                absen_langsung(form_url, nama)
        with c7:
            if st.button("S", key=f"s_{prefix}_{i}", disabled=is_pagi_range):
                absen_langsung(form_url, nama)

tab1, tab2 = st.tabs(["👥 PEGAWAI PNS", "👥 PEGAWAI PPPK"])
with tab1: render_list(fetch_data(URL_CSV_PNS), MASTER_DATA["PNS"], FORM_URL_PNS, "pns")
with tab2: render_list(fetch_data(URL_CSV_PPPK), MASTER_DATA["PPPK"], FORM_URL_PPPK, "pppk")
