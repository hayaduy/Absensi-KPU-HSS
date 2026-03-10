import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Absensi KPU HSS", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS FINAL
st.markdown("""
    <style>
    .stApp { background-color: #2d0a0a; color: #ffffff; }
    .header-jam { text-align: center; padding: 20px 0; }
    .clock-text { font-size: 70px; font-weight: bold; color: #ffffff; text-shadow: 0 0 20px rgba(255,255,255,0.6); }
    
    div[data-testid="stDateInput"] { width: 300px !important; margin: 0 auto !important; }
    div[data-testid="stDateInput"] label { display: none; }

    div.stButton { display: flex; justify-content: center; width: 100%; }
    div.stButton > button:first-child { 
        background: linear-gradient(90deg, #f97316 0%, #ea580c 100%) !important; 
        color: white !important; width: 100% !important; max-width: 450px !important; 
        height: 60px !important; font-size: 20px !important; font-weight: 800 !important; 
        border-radius: 15px !important; border: 1px solid #fb923c !important;
        box-shadow: 0 0 15px rgba(234, 88, 12, 0.4) !important; margin-top: 15px;
    }

    .stTabs [data-baseweb="tab-list"] { justify-content: center !important; gap: 5px; border: none !important; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #4c0519 !important; border-radius: 12px 12px 0 0 !important; 
        padding: 12px 40px !important; color: #fca5a5 !important;
    }
    .stTabs [aria-selected="true"] { background-color: #f97316 !important; color: #ffffff !important; }

    .row-container {
        display: flex; align-items: center;
        background: linear-gradient(90deg, #4c0519 0%, #7f1d1d 100%);
        padding: 15px 25px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #991b1b;
        max-width: 1100px; margin-left: auto; margin-right: auto;
    }

    .col-nama { flex: 4; font-size: 18px; font-weight: 700; }
    .col-nama a { color: #fecaca; text-decoration: none; display: block; width: 100%; }
    .col-data-wrap { flex: 5; display: flex; justify-content: space-around; text-align: center; border-left: 1px solid #991b1b; padding: 0 30px; }
    .val-v { font-size: 16px; font-weight: 800; color: #ffffff; }
    .label-k { font-size: 10px; color: #fca5a5; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# 3. MASTER DATA
MASTER_DATA = {
    "PNS": ["Suwanto, SH., MH.", "Wawan Setiawan, SH", "Ineke Setiyaningsih, S.Sos", "Farah Agustina Setiawati, SH", "Rusma Ariati, SE", "Helmalina", "Ahmad Erwan Rifani, S.HI", "Syaiful Anwar", "Zainal Hilmi Yustan", "Najmi Hidayati", "Jainal Abidin", "Suci Lestari, S.Ikom", "Athaya Insyira Khairani, S.H", "Muhammad Ibnu Fahmi, S.H.", "Alfian Ridhani, S.Kom", "Muhammad Aldi Hudaifi, S.Kom", "Firda Aulia, S.Kom."],
    "PPPK": ["Sya'bani Rona Baika", "Apriadi Rakhman", "M Satria Maipadly", "Basuki Rahmat", "Sulaiman", "Saldoz Yedi", "Mastoni Ridani", "Suriadi", "Ami Aspihani", "Abdurrahman", "Emaliani", "Muhammad Hafiz Rijani, S.KOM", "Saiful Fahmi, S.Pd", "Nadianti"]
}

URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"
E_ID = "960346359"

# 4. JAM & KONTROL
wita_now = datetime.now() + timedelta(hours=8)
st.markdown(f'<div class="header-jam"><div class="clock-text">{wita_now.strftime("%H:%M:%S")}</div></div>', unsafe_allow_html=True)

# 5. FUNGSI LOGIKA
def fetch_data(url):
    try:
        res = requests.get(f"{url}&nc={random.random()}", timeout=10)
        df = pd.read_csv(StringIO(res.text))
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], dayfirst=True)
        return df
    except: return pd.DataFrame()

def render_list(df, master, form_url, tgl_pilihan):
    today_str = tgl_pilihan.strftime('%d/%m/%Y')
    wita_current = datetime.now() + timedelta(hours=8)
    log = {}
    
    if not df.empty:
        mask = df.iloc[:, 0].dt.strftime('%d/%m/%Y') == today_str
        df_today = df[mask]
        for _, r in df_today.iterrows():
            nama, dt = str(r.iloc[1]).strip(), r.iloc[0]
            jam = dt.time()
            if nama not in log:
                status = "HADIR" if jam.hour < 9 else "TERLAMBAT"
                log[nama] = {"m": jam.strftime("%H:%M"), "p": "--:--", "k": status}
            elif jam.hour >= 16: log[nama]["p"] = jam.strftime("%H:%M")

    for i, p in enumerate(sorted(master), 1):
        nama_p = p.strip()
        if nama_p in log: d = log[nama_p]
        else:
            if tgl_pilihan < wita_current.date(): ket = "ALPA"
            elif wita_current.hour >= 16: ket = "LAPOR KASUBBAG"
            elif wita_current.hour >= 9: ket = "TERLAMBAT"
            else: ket = "BELUM ABSEN"
            d = {"m": "--:--", "p": "--:--", "k": ket}

        clr = "#4ade80" if d["k"]=="HADIR" else "#60a5fa" if d["k"]=="BELUM ABSEN" else "#fb923c" if d["k"]=="TERLAMBAT" else "#f87171"
        link = f"{form_url}?entry.{E_ID}={p.replace(' ', '+')}&submit=Submit"
        st.markdown(f'<div class="row-container"><div class="col-nama"><a href="{link}" target="_self">{i}. {p.split(",")[0]}</a></div><div class="col-data-wrap"><div class="item-box"><div class="label-k">Pagi</div><div class="val-v">{d["m"]}</div></div><div class="item-box"><div class="label-k">Sore</div><div class="val-v">{d["p"]}</div></div><div class="item-box"><div class="label-k">Ket</div><div style="color:{clr}; font-weight:900;">{d["k"]}</div></div></div></div>', unsafe_allow_html=True)

# 6. TABS LAYOUT
tgl_pilihan = st.date_input("Tanggal", wita_now.date(), label_visibility="collapsed")
tab1, tab2, tab3 = st.tabs(["👥 PNS", "👥 PPPK", "📊 REKAP BULANAN"])

df_pns = fetch_data(URL_PNS)
df_pppk = fetch_data(URL_PPPK)

with tab1:
    render_list(df_pns, MASTER_DATA["PNS"], FORM_PNS, tgl_pilihan)

with tab2:
    render_list(df_pppk, MASTER_DATA["PPPK"], FORM_PPPK, tgl_pilihan)

with tab3:
    st.markdown("### 📊 Rekapitulasi Kehadiran Pegawai")
    c1, c2, c3 = st.columns([2, 2, 2])
    with c1: bulan = st.selectbox("Bulan", list(range(1, 13)), index=wita_now.month-1)
    with c2: tahun = st.selectbox("Tahun", [2024, 2025, 2026], index=2)
    
    all_data = pd.concat([df_pns, df_pppk])
    if not all_data.empty:
        # Filter data bulan/tahun
        report_df = all_data[(all_data.iloc[:, 0].dt.month == bulan) & (all_data.iloc[:, 0].dt.year == tahun)].copy()
        report_df['Nama'] = report_df.iloc[:, 1].str.strip()
        report_df['Jam'] = report_df.iloc[:, 0].dt.hour
        
        rekap = []
        for kategori, daftar in MASTER_DATA.items():
            for nama in daftar:
                p_data = report_df[report_df['Nama'] == nama.strip()]
                # Logika: Hadir tepat (sebelum jam 9), Terlambat (jam 9 ke atas)
                # Dihitung per hari unik
                h_tepat = p_data[p_data['Jam'] < 9].iloc[:, 0].dt.date.nunique()
                h_telat = p_data[p_data['Jam'] >= 9].iloc[:, 0].dt.date.nunique()
                rekap.append({
                    "Nama Pegawai": nama,
                    "Kategori": kategori,
                    "Hadir Tepat": h_tepat,
                    "Terlambat": h_telat,
                    "Total Hadir": h_tepat + h_telat
                })
        
        final_rekap = pd.DataFrame(rekap)
        
        # Fitur Urutkan
        with c3: sort_by = st.selectbox("Urutkan:", ["Total Hadir", "Hadir Tepat", "Terlambat", "Nama Pegawai"])
        final_rekap = final_rekap.sort_values(by=sort_by, ascending=(False if sort_by != "Nama Pegawai" else True))
        
        # Tampilkan Tabel
        st.dataframe(final_rekap, use_container_width=True, hide_index=True)
        
        # Tombol Download
        csv = final_rekap.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 DOWNLOAD REKAP (CSV)",
            data=csv,
            file_name=f'rekap_absen_{bulan}_{tahun}.csv',
            mime='text/csv',
        )
    else:
        st.warning("Data tidak ditemukan untuk periode ini.")

if st.button("🔍 REFRESH SISTEM"):
    st.rerun()

time.sleep(30)
st.rerun()
