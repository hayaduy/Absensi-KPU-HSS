import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Monitoring Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS SAKTI: FULL FREEZE & CLEAN UI (FIX SCROLL & MOBILE)
st.markdown("""
    <style>
    /* Dasar & Background */
    .stApp { background-color: #1a0505; color: #ffffff; overflow: hidden; }
    
    /* Hilangkan Header Bawaan Streamlit agar tidak bentrok */
    header[data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .block-container { padding: 0rem !important; max-width: 100% !important; height: 100vh; display: flex; flex-direction: column; }

    /* --- FULL FREEZE SECTION (JAM, RUNNING TEXT, TANGGAL, & TABS) --- */
    #freeze-header {
        background-color: #1a0505;
        border-bottom: 3px solid #7f1d1d;
        padding: 10px 10px 5px 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }

    .header-jam { text-align: center; }
    .clock-text { 
        font-size: clamp(40px, 12vw, 85px); 
        font-weight: 900; color: #ffffff; 
        text-shadow: 0 0 25px rgba(249, 115, 22, 0.5); 
        font-family: 'Courier New', Courier, monospace;
        margin: 0;
    }
    
    /* Running Text */
    .running-text-container { 
        width: 100%; overflow: hidden; margin: 10px 0; 
        background: rgba(0,0,0,0.3); padding: 8px 0; border-radius: 8px; 
    }
    .running-text { font-size: clamp(12px, 3.5vw, 17px); font-weight: 600; color: #ffffff; white-space: nowrap; animation: scroll-left 30s linear infinite; display: inline-block; }
    .highlight { color: #facc15; font-weight: 800; text-shadow: 0 0 10px rgba(250, 204, 21, 0.4); }
    @keyframes scroll-left { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    /* Input Tanggal Center */
    div[data-testid="stDateInput"] {
        width: 100% !important; max-width: 320px !important; margin: 5px auto !important;
        background: rgba(45, 10, 10, 0.9); border: 2px solid #f97316; border-radius: 12px; padding: 5px;
    }
    div[data-testid="stDateInput"] label { display: none; }
    div[data-testid="stDateInput"] input { color: #ffffff !important; text-align: center !important; background-color: transparent !important; border: none !important; font-size: 19px !important; font-weight: bold !important; }

    /* TAB Menu Center */
    .stTabs [data-baseweb="tab-list"] { 
        justify-content: center !important; 
        background-color: transparent !important;
        gap: clamp(5px, 2vw, 20px) !important;
    }
    .stTabs [data-baseweb="tab"] { font-size: clamp(11px, 3vw, 14px) !important; padding: 10px 15px !important; color: #fca5a5 !important;}
    .stTabs [aria-selected="true"] { color: #ffffff !important; font-weight: bold; }

    /* --- SCROLLABLE CONTENT SECTION --- */
    /* Membuat area konten di bawah tab bisa di-scroll secara independen */
    [data-baseweb="tab-panel"] {
        overflow-y: auto;
        flex: 1;
        padding: 20px 10px 50px 10px !important;
        background-color: rgba(26, 5, 5, 0.5);
    }
    /* Sembunyikan scrollbar di Chrome/Safari */
    [data-baseweb="tab-panel"]::-webkit-scrollbar { width: 0px; background: transparent; }

    /* ROW PEGAWAI */
    .row-container {
        display: flex; flex-direction: column; 
        background: linear-gradient(90deg, #2d0a0a 0%, #4c0519 100%);
        padding: 15px; border-radius: 18px; margin-bottom: 15px; border: 1px solid #7f1d1d;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.3);
        max-width: 1100px; margin-left: auto; margin-right: auto;
    }
    
    @media (min-width: 768px) {
        .row-container { flex-direction: row; align-items: center; justify-content: space-between; padding: 15px 30px; }
        .col-nama { flex: 4; text-align: left; margin-bottom: 0; }
        .col-data-wrap { flex: 6; border-top: none; border-left: 1px solid rgba(127, 29, 29, 0.5); padding-top: 0; padding-left: 20px; }
    }

    .col-nama { width: 100%; text-align: center; margin-bottom: 12px; }
    .name-box { 
        background: rgba(249, 115, 22, 0.08); padding: 10px 20px; 
        border: 1px solid rgba(249, 115, 22, 0.15); border-radius: 12px; 
        display: inline-block; width: 100%; max-width: 380px; 
    }
    .name-box a { color: #fecaca !important; text-decoration: none !important; font-size: 18px; font-weight: 700; }
    .name-box:hover { background: rgba(249, 115, 22, 0.15); border-color: #f97316; transition: 0.3s; }

    .col-data-wrap { 
        width: 100%; display: flex; justify-content: space-around; 
        text-align: center; border-top: 1px solid rgba(127, 29, 29, 0.5); padding-top: 15px;
    }
    .val-v { font-size: clamp(16px, 4.5vw, 19px); font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 1px;}
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA DENGAN URUTAN HIRARKI (STRUKTURAL)
# Najmi Hidayati sudah dikoreksi
MASTER_PNS = [
    "Suwanto, SH., MH.",           # Sekretaris
    "Wawan Setiawan, SH",          # Kasubbag
    "Ineke Setiyaningsih, S.Sos",   # Kasubbag
    "Farah Agustina Setiawati, SH", # Kasubbag
    "Rusma Ariati, SE",            # Kasubbag
    "Helmalina", 
    "Ahmad Erwan Rifani, S.HI", 
    "Syaiful Anwar", 
    "Zainal Hilmi Yustan", 
    "Najmi Hidayati", 
    "Jainal Abidin", 
    "Suci Lestari, S.Ikom", 
    "Athaya Insyira Khairani, S.H", 
    "Muhammad Ibnu Fahmi, S.H.", 
    "Alfian Ridhani, S.Kom", 
    "Muhammad Aldi Hudaifi, S.Kom", 
    "Firda Aulia, S.Kom."
]

MASTER_PPPK = [
    "Sya'bani Rona Baika", 
    "Apriadi Rakhman", 
    "M Satria Maipadly", 
    "Basuki Rahmat", 
    "Sulaiman", 
    "Saldoz Yedi", 
    "Mastoni Ridani", 
    "Suriadi", 
    "Ami Aspihani", 
    "Abdurrahman", 
    "Emaliani", 
    "Muhammad Hafiz Rijani, S.KOM", 
    "Saiful Fahmi, S.Pd", 
    "Nadianti"
]

# Gabungan Hirarki untuk Tab Semua
MASTER_ALL_HIERARCHY = MASTER_PNS + MASTER_PPPK

# Link Sumber Data
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
# Link Form Pre-filled
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
ENTRY_ID = "960346359" # ID field nama di Google Form

# 4. ENGINE PROSES SAKTI (ANTI-ERROR & MEMBERSIHKAN TANGGAL)
def fetch_raw(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        return pd.read_csv(StringIO(res.text))
    except: return pd.DataFrame()

@st.cache_data(ttl=20) # Cache data selama 20 detik agar tidak overload sheets
def load_and_clean_all():
    df_pns = fetch_raw(URL_PNS)
    df_pppk = fetch_raw(URL_PPPK)
    
    # Fungsi pembersih sakti untuk kolom Timestamp
    def clean_timestamps(df):
        if df.empty: return df
        # Gunakan nama kolom pertama sebagai Kolom Timestamp
        ts_col = df.columns[0]
        # Konversi ke string dulu, bersihkan spasi, baru ubah ke datetime
        df[ts_col] = df[ts_col].astype(str).str.strip()
        # errors='coerce' akan mengubah data rusak menjadi NaT (Not a Time)
        df[ts_col] = pd.to_datetime(df[ts_col], dayfirst=True, errors='coerce')
        # Hapus data yang rusak (NaT) agar tidak bikin error saat .dt
        return df.dropna(subset=[ts_col])

    return clean_timestamps(df_pns), clean_timestamps(df_pppk)

# 5. HEADER FULL FREEZE AREA (PAKSA Z-INDEX)
with st.container():
    st.markdown('<div id="freeze-header">', unsafe_allow_html=True)
    # Placeholder untuk Jam (diupdate oleh loop realtime)
    clock_placeholder = st.empty()
    
    # Input Tanggal (Bagian dari Fixed Header)
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        wita_now = datetime.now() + timedelta(hours=8)
        tgl_pilihan = st.date_input("Tanggal", wita_now.date(), key="main_date_input")
    
    # Tab Menu (Diletakkan di dalam container yang di-freeze secara visual)
    st.markdown('<div class="center-tabs">', unsafe_allow_html=True)
    tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA PEGAWAI", "👥 PNS", "👥 PPPK"])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. LOGIKA DATA PROSES
def get_log(df, tgl):
    today = tgl.strftime('%Y-%m-%d'); log = {}
    if not df.empty:
        ts_col = df.columns[0]; nm_col = df.columns[1]
        # Filter aman berdasarkan tanggal yang sudah dibersihkan
        df_today = df[df[ts_col].dt.normalize() == pd.Timestamp(tgl)]
        df_sorted = df_today.sort_values(by=ts_col)
        
        for _, r in df_sorted.iterrows():
            ts = r[ts_col]; nama = str(r[nm_col]).strip().replace("  ", " ")
            if nama not in log:
                log[nama] = {"m": ts.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if ts.hour < 9 else "TERLAMBAT"}
            elif ts.hour >= 15: log[nama]["p"] = ts.strftime("%H:%M")
    return log

def render_list_item(log, master_list, form_url_pns, form_url_pppk, combined=False, current_wita=wita_now):
    items_to_render = []
    
    for idx, p in enumerate(master_list):
        nama_p = p.strip().replace("  ", " ")
        # Data default jika belum absen
        d = log.get(nama_p, {"m": "--:--", "p": "--:--", "k": "BELUM ABSEN"})
        
        # Logika Status Dinamis
        if d["k"] == "BELUM ABSEN":
            if tgl_pilihan < current_wita.date(): d["k"] = "ALPA"
            elif current_wita.hour >= 16: d["k"] = "LAPOR KASUBBAG"
            elif current_wita.hour >= 9: d["k"] = "TERLAMBAT"
            
        # Tentukan Bobot (Priority 0 untuk yang belum absen agar naik)
        priority_weight = 1 if d["k"] in ["HADIR", "TERLAMBAT"] and d["m"] != "--:--" else 0
        items_to_render.append({"n": nama_p, "d": d, "w": priority_weight, "h": idx})

    # Logika Sorting jika di tab 'Semua' (sort_priority=True)
    if combined:
        items_to_render = sorted(items_to_render, key=lambda x: (x['w'], x['h']))
    else:
        items_to_render = sorted(items_to_render, key=lambda x: x['h'])

    for item in items_to_render:
        n = item["n"]; d = item["d"]; cl = "#4ade80" if d["k"]=="HADIR" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        # Tentukan Form Link berdasarkan Hirarki
        target_form = form_url_pns if n in MASTER_PNS else form_url_pppk
        link = f"{target_form}?entry.{ENTRY_ID}={n.replace(' ', '+')}&submit=Submit"
        
        st.markdown(f"""
        <div class="row-container">
            <div class="col-nama">
                <div class="name-box"><a href="{link}" target="_blank">{n.split(',')[0]}</a></div>
            </div>
            <div class="col-data-wrap">
                <div><div class="label-k">Pagi</div><div class="val-v">{d['m']}</div></div>
                <div><div class="label-k">Sore</div><div class="val-v">{d['p']}</div></div>
                <div><div class="label-k">Ket</div><div style="color:{clr}; font-weight:900;">{d['k']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 7. MENAMPILKAN DATA DI TABS (SCROLLABLE AREA)
df_cleaned_pns, df_cleaned_pppk = load_and_clean_all()
log_data_pns = get_log(df_cleaned_pns, tgl_pilihan)
log_data_pppk = get_log(df_cleaned_pppk, tgl_pilihan)
log_combined = {**log_data_pns, **log_data_pppk}

with tab_all:
    # combined=True agar yang belum absen naik ke atas
    render_list_item(log_combined, MASTER_ALL_HIERARCHY, FORM_PNS, FORM_PPPK, combined=True, current_wita=wita_now)

with tab_pns:
    render_list_item(log_data_pns, MASTER_PNS, FORM_PNS, FORM_PPPK, combined=False, current_wita=wita_now)

with tab_pppk:
    render_list_item(log_data_pppk, MASTER_PPPK, FORM_PNS, FORM_PPPK, combined=False, current_wita=wita_now)

# 8. UPDATE HEADER REALTIME (JAM & REFRESH 60 DETIK)
while True:
    now = datetime.now() + timedelta(hours=8)
    clock_placeholder.markdown(f"""
        <div class="header-jam">
            <div class="clock-text">{now.strftime("%H:%M:%S")}</div>
            <div class="running-text-container">
                <div class="running-text">
                    ABSENSI KPU Kabupaten Hulu Sungai Selatan &nbsp; • &nbsp; 
                    <span class="highlight">Silahkan Cek Kehadiran hari ini yaa, Klik Nama masing-masing untuk Absen</span> &nbsp; • &nbsp; 
                    KPU Kabupaten Hulu Sungai Selatan
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Auto Update otomatis setiap menit ke-0 (1 menit sekali)
    if now.second == 0:
        st.cache_data.clear() # Paksa clear cache agar dataSheets terbaru diambil
        st.rerun()
        
    time.sleep(1)
