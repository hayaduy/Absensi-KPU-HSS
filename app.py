import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# --- CSS: BIG BOX BUTTONS & CLEAN TABLE ---
st.markdown("""
    <style>
    .centered { text-align: center; width: 100%; }
    .clock-style { font-size: 55px; color: #3498db; font-weight: bold; margin-bottom: 0px; }
    
    /* Tombol Cek Data Terbaru Tengah */
    div.stButton > button:first-child {
        background-color: #d35400 !important;
        color: white !important;
        width: 85% !important;
        height: 60px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        margin: 10px auto !important;
        display: block !important;
        border-radius: 10px !important;
    }

    /* Styling Link Tombol agar jadi Kotak Gede */
    .absen-link {
        display: block;
        width: 100%;
        height: 50px;
        line-height: 50px;
        text-align: center;
        background-color: #2980b9;
        color: white !important;
        text-decoration: none;
        font-weight: bold;
        border-radius: 8px;
        font-size: 18px;
    }
    .absen-sore { background-color: #e67e22; }
    .absen-off { background-color: #444; color: #888 !important; pointer-events: none; }

    /* Kolom Sejajar */
    .stHorizontalBlock { align-items: center !important; border-bottom: 1px solid #333; padding: 5px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- MASTER DATA (Sesuai Foto Excel Abang) ---
# Format: "Nama": "NIP"
MASTER_PNS = {
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
}

MASTER_PPPK = {
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

URL_PNS_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

# Pre-filled Link Generator
def get_link(base_url, nama):
    import urllib.parse
    return f"{base_url}{urllib.parse.quote(nama)}"

FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/viewform?entry.960346359="
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/viewform?entry.960346359="

# --- TIME ---
wita_now = datetime.now() + timedelta(hours=8)
is_pagi_range = wita_now.hour < 16

st.markdown("<h3 class='centered'>📊 MONITORING ABSENSI KPU HSS</h3>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

col_a, col_b, col_c = st.columns([1, 4, 1])
with col_b:
    tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
    if st.button("🔍 CEK DATA TERBARU"): st.rerun()

def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        return df.dropna(subset=[df.columns[0]])
    except: return pd.DataFrame()

def render_list(df, master_dict, form_base, prefix):
    t_batas = datetime.strptime("09:00", "%H:%M").time()
    t_pulang = datetime.strptime("16:00", "%H:%M").time()
    log = {}
    
    if not df.empty:
        tgl_target = tgl_pilihan.strftime('%d/%m/%Y')
        tgl_target_alt = tgl_pilihan.strftime('%Y-%m-%d')
        for _, r in df.iterrows():
            ts = str(r.iloc[0])
            if tgl_target in ts or tgl_target_alt in ts:
                try:
                    dt_obj = pd.to_datetime(ts, dayfirst=True)
                    nama, jam = str(r.iloc[1]).strip(), dt_obj.time()
                    if nama not in log:
                        status = "HDR" if jam <= t_batas else "TLT"
                        log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": status}
                    elif jam >= t_pulang:
                        log[nama]["p"] = jam.strftime("%H:%M")
                except: continue

    st.write("---")
    h1, h2, h3, h4, h5, h6, h7 = st.columns([0.5, 3.5, 1, 1, 0.8, 1, 1])
    h1.write("**#**"); h2.write("**NAMA**"); h3.write("**PAGI**"); h4.write("**SORE**"); h5.write("**ST**"); h6.write("**P**"); h7.write("**S**")
    
    for i, (nama, nip) in enumerate(master_dict.items(), 1):
        d = log.get(nama.strip(), {"m": "--", "p": "--", "k": "ALPA"})
        clr = "green" if d["k"]=="HDR" else "orange" if d["k"]=="TLT" else "red"
        
        c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 3.5, 1, 1, 0.8, 1, 1])
        c1.write(f"{i}")
        c2.write(f"**{nama.split(',')[0]}**")
        c3.write(d["m"])
        c4.write(d["p"])
        c5.markdown(f":{clr}[**{d['k']}**]")
        
        link_pagi = get_link(form_base, nama)
        link_sore = get_link(form_base, nama)
        
        with c6:
            p_style = "absen-link" if is_pagi_range else "absen-link absen-off"
            st.markdown(f"<a href='{link_pagi}' target='_blank' class='{p_style}'>P</a>", unsafe_allow_html=True)
        with c7:
            s_style = "absen-link absen-sore" if not is_pagi_range else "absen-link absen-off"
            st.markdown(f"<a href='{link_sore}' target='_blank' class='{s_style}'>S</a>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👥 PNS", "👥 PPPK"])
with tab1: render_list(fetch_data(URL_PNS_CSV), MASTER_PNS, FORM_PNS, "pns")
with tab2: render_list(fetch_data(URL_PPPK_CSV), MASTER_PPPK, FORM_PPPK, "pppk")
