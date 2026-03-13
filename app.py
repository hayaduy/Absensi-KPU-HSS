import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO
import urllib3
import urllib.parse
import pytz

# Import library tambahan untuk auto-refresh
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Absensi KPU HSS", page_icon="🚀", layout="wide")

# --- DATABASE LIBUR NASIONAL 2026 ---
LIBUR_NASIONAL_2026 = {
    "2026-01-01": "TAHUN BARU 2026",
    "2026-01-19": "ISRA MI'RAJ",
    "2026-02-17": "TAHUN BARU IMLEK",
    "2026-03-20": "HARI RAYA NYEPI",
    "2026-03-20": "IDUL FITRI 1447 H",
    "2026-03-21": "IDUL FITRI 1447 H",
    "2026-04-03": "WAFAT YESUS KRISTUS",
    "2026-05-01": "HARI BURUH",
    "2026-05-14": "KENAIKAN YESUS KRISTUS",
    "2026-05-22": "HARI RAYA WAISAK",
    "2026-05-27": "IDUL ADHA 1447 H",
    "2026-06-01": "HARI LAHIR PANCASILA",
    "2026-06-16": "TAHUN BARU ISLAM 1448 H",
    "2026-08-17": "HARI KEMERDEKAAN RI",
    "2026-08-25": "MAULID NABI MUHAMMAD",
    "2026-12-25": "HARI RAYA NATAL"
}
LIST_HARI = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]

# --- DATABASE PEGAWAI ---
DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris KPU"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum dan SDM"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER AHLI PERTAMA"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER AHLI PERTAMA"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Basuki Rahmat": ["197705222024211007", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN OPERASIONAL"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN OPERASIONAL"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM OPERASIONAL"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN OPERASIONAL"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN OPERASIONAL"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI PERKANTORAN"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN"]
}

MASTER_PNS = list(DATABASE_INFO.keys())[:17]
MASTER_PPPK = list(DATABASE_INFO.keys())[17:]

# 3. CSS LUXURY
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #0f0202 0%, #1a0505 100%); color: #ffffff; }
    .header-box { text-align: center; padding: 20px 0 10px 0; }
    .clock-text { font-size: clamp(55px, 10vw, 85px); font-weight: 900; color: #ffffff; text-shadow: 0 0 40px rgba(249, 115, 22, 0.7); line-height: 1; }
    .date-text { font-size: clamp(18px, 3vw, 24px); color: #f97316; font-weight: 500; margin-top: 5px; letter-spacing: 2px; }
    .holiday-header { font-size: 18px; font-weight: 800; color: #3b82f6; text-transform: uppercase; margin-top: 5px; }

    div.stButton > button {
        background: rgba(255, 255, 255, 0.03) !important; color: #f1f5f9 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important; 
        font-weight: 600 !important; text-align: left !important; 
        padding-left: 20px !important; height: 64px !important; border-radius: 18px !important;
    }
    div.stButton > button:disabled { background: rgba(255, 255, 255, 0.01) !important; opacity: 0.3 !important; border: 1px solid transparent !important; }
    
    .label-k { font-size: 11px; color: #94a3b8; text-transform: uppercase; }
    .val-v { font-size: 19px; font-weight: 800; color: #ffffff; }
    .status-hadir { color: #4ade80; font-weight: 900; }
    .status-lupa { color: #fb923c; font-weight: 900; }
    .status-belum { color: #f87171; font-weight: 900; }
    .status-libur { color: #3b82f6; font-weight: 900; }

    .marquee-container {
        position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(15, 2, 2, 0.95); backdrop-filter: blur(15px);
        padding: 14px 0; border-top: 1px solid rgba(249, 115, 22, 0.3); z-index: 1000; overflow: hidden;
    }
    .marquee-text { display: inline-block; white-space: nowrap; animation: scroll 30s linear infinite; -webkit-animation: scroll 30s linear infinite; font-size: 15px; font-weight: 600; color: #fca5a5; }
    @keyframes scroll { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNGSI DATA
def get_wita(): return datetime.utcnow() + timedelta(hours=8)

@st.cache_data(ttl=15)
def fetch_raw(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        return pd.read_csv(StringIO(res.text))
    except: return pd.DataFrame()

def process_log(df, tgl):
    log = {}; target = tgl.strftime('%d/%m/%Y')
    if not df.empty:
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True, errors='coerce')
        df = df.dropna(subset=[df.columns[0]]).sort_values(by=df.columns[0])
        for _, r in df.iterrows():
            ts = r.iloc[0]
            if ts.strftime('%d/%m/%Y') == target:
                n = str(r.iloc[1]).strip()
                if n not in log: log[n] = {"m": ts.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if ts.hour < 9 else "LUPA ABSEN"}
                if ts.hour >= 15: log[n]["p"] = ts.strftime("%H:%M")
    return log

# 5. UI HEADER & HOLIDAY LOGIC
wita_now = get_wita()
day_name = LIST_HARI[wita_now.weekday()]
date_key = wita_now.strftime("%Y-%m-%d")
is_weekend = wita_now.weekday() >= 5
holiday_name = LIBUR_NASIONAL_2026.get(date_key)

# Header Display
st.markdown(f"""
    <div class="header-box">
        <div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div>
        <div class="date-text">{wita_now.strftime("%A, %d %B %Y").upper()}</div>
        <div class="holiday-header">{f"{day_name}, LIBUR ({holiday_name})" if holiday_name else f"{day_name}, LIBUR (AKHIR PEKAN)" if is_weekend else f"{day_name}, HARI KERJA"}</div>
    </div>
""", unsafe_allow_html=True)

tgl_pilihan = st.date_input("Filter", wita_now.date(), label_visibility="collapsed")
is_locked = (LIBUR_NASIONAL_2026.get(tgl_pilihan.strftime("%Y-%m-%d")) is not None) or (tgl_pilihan.weekday() >= 5)

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
log_all = {**process_log(fetch_raw(URL_PNS), tgl_pilihan), **process_log(fetch_raw(URL_PPPK), tgl_pilihan)}

# 6. MODAL KONFIRMASI
@st.dialog("Konfirmasi Kehadiran")
def show_confirm_modal(n):
    form_id = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA" if n in MASTER_PNS else "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
    info = DATABASE_INFO.get(n)
    nama_enc = urllib.parse.quote_plus(n)
    nip_enc = urllib.parse.quote_plus(info[0])
    jab_enc = urllib.parse.quote_plus(info[1])
    url_submit = f"https://docs.google.com/forms/d/e/{form_id}/formResponse?entry.960346359={nama_enc}&entry.468881973={nip_enc}&entry.159009649={jab_enc}&submit=Submit"
    st.subheader(f"{n}")
    st.write(f"Jabatan: {info[1]}")
    st.markdown(f"""<br><a href="{url_submit}" target="_self" style="text-decoration: none; display: block; background: linear-gradient(90deg, #f97316, #ea580c); color: white; text-align: center; padding: 18px; border-radius: 15px; font-weight: 800; font-size: 18px; box-shadow: 0 10px 25px rgba(249,115,22,0.4);">KONFIRMASI & KIRIM ✅</a>""", unsafe_allow_html=True)

# 7. RENDER LIST
def render_list(log, master_list, tab_id):
    curr_h_name = LIBUR_NASIONAL_2026.get(tgl_pilihan.strftime("%Y-%m-%d"))
    curr_weekend = tgl_pilihan.weekday() >= 5
    
    for idx, n in enumerate(master_list):
        if n in log: d = log[n]
        elif curr_h_name: d = {"m": "--:--", "p": "--:--", "k": "LIBUR"}
        elif curr_weekend: d = {"m": "--:--", "p": "--:--", "k": "LIBUR"}
        else: d = {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"}
        
        cl_class = "status-hadir" if d["k"]=="HADIR" else "status-libur" if d["k"]=="LIBUR" else "status-lupa" if "LUPA" in d["k"] else "status-belum"
        c1, c2, c3, c4 = st.columns([4, 2, 2, 2])
        with c1:
            if st.button(f"👤 {n.split(',')[0]}", key=f"btn_{tab_id}_{idx}", use_container_width=True, disabled=is_locked):
                show_confirm_modal(n)
        with c2: st.markdown(f"<div style='text-align:center'><div class='label-k'>Pagi</div><div class='val-v'>{d['m']}</div></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div style='text-align:center'><div class='label-k'>Sore</div><div class='val-v'>{d['p']}</div></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div style='text-align:center'><div class='label-k'>Ket</div><div class='{cl_class}'>{d['k']}</div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='margin:8px 0; border:0; border-top: 1px solid rgba(255,255,255,0.05)'>", unsafe_allow_html=True)

# 8. TABS
st.markdown("<br>", unsafe_allow_html=True)
t1, t2, t3 = st.tabs(["🌎 SEMUA (31)", "👥 PNS (17)", "👥 PPPK (14)"])
with t1: render_list(log_all, list(DATABASE_INFO.keys()), "tab1")
with t2: render_list(log_all, MASTER_PNS, "tab2")
with t3: render_list(log_all, MASTER_PPPK, "tab3")

# 9. FOOTER (RUNNING TEXT DYNAMIC)
if is_locked:
    h_info = LIBUR_NASIONAL_2026.get(tgl_pilihan.strftime("%Y-%m-%d")) or "AKHIR PEKAN"
    marquee_msg = f"🛡️ SISTEM TERKUNCI: HARI INI ADALAH {h_info} --- SELAMAT BERISTIRAHAT DENGAN TENANG, COY! ☕ --- TETAP JAGA KESEHATAN"
else:
    marquee_msg = f"🔴 MONITORING ABSENSI SEKRETARIAT KPU KAB. HSS --- JANGAN LUPA ABSEN PAGI DAN SORE --- TETAP SEMANGAT BEKERJA UNTUK NEGERI --- DATA TER-UPDATE SECARA OTOMATIS --- JAM WITA: {wita_now.strftime('%H:%M')}"

st.markdown(f"""<div class="marquee-container"><div class="marquee-text">{marquee_msg} &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; {marquee_msg}</div></div><br><br><br>""", unsafe_allow_html=True)

# 10. AUTO REFRESH
if st_autorefresh:
    st_autorefresh(interval=600000, key="auto_refresh_pwa")
