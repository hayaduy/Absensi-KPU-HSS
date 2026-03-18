import streamlit as st
import pandas as pd
import requests
from io import StringIO, BytesIO
from datetime import datetime
import calendar
import pytz
import random
import time

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="KPU HSS Presence Hub v90.0", layout="wide", page_icon="🏛️")
wita_tz = pytz.timezone('Asia/Makassar')

LIBUR_DAN_CUTI_2026 = {
    "2026-01-01": "Tahun Baru 2026", "2026-01-19": "Isra Mi'raj", "2026-02-17": "Imlek",
    "2026-03-18": "Cuti Nyepi", "2026-03-19": "Cuti Nyepi", "2026-03-20": "Hari Nyepi",
    "2026-03-21": "Idul Fitri", "2026-03-22": "Idul Fitri", "2026-03-23": "Cuti Idul Fitri",
    "2026-03-24": "Cuti Idul Fitri", "2026-03-25": "Cuti Idul Fitri", "2026-04-03": "Wafat Yesus",
    "2026-05-01": "Hari Buruh", "2026-05-14": "Kenaikan Yesus", "2026-05-22": "Waisak",
    "2026-06-01": "Hari Lahir Pancasila", "2026-08-17": "HUT RI", "2026-12-25": "Natal"
}

LIST_BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

st.markdown("""
    <style>
    /* Layout Utama */
    .stApp { background: linear-gradient(135deg, #450a0a 0%, #000000 50%, #7c2d12 100%); background-attachment: fixed; }
    .block-container { max-width: 1050px; padding-top: 5rem !important; }
    .header-box { text-align: center; color: #F59E0B; font-size: 32px; font-weight: bold; margin-bottom: 5px; }
    .clock-box { text-align: center; color: white; font-size: 18px; margin-bottom: 25px; font-family: monospace; }
    .employee-card { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); padding: 10px 20px; border-radius: 12px; display: flex; align-items: center; margin-bottom: 5px; border: 1px solid rgba(255, 255, 255, 0.1); }
    .emp-name { flex: 3; color: white; font-weight: bold; font-size: 14px; }
    .emp-time { flex: 1.2; color: #cbd5e1; text-align: center; font-size: 13px; }
    .emp-status { flex: 1; text-align: right; font-weight: bold; font-size: 13px; }
    .status-hadir { color: #10B981; }
    .status-alpa { color: #EF4444; }
    .status-terlambat { color: #F59E0B; }
    .stButton>button { background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(5px); border: 1px solid rgba(255, 255, 255, 0.2) !important; color: white !important; border-radius: 8px; font-weight: bold; }
    [data-testid="stSidebar"] { display: none; }
    
    /* FIX POP UP UNTUK SMARTPHONE - DARK THEME SOLID */
    div[data-testid="stDialog"] div[role="dialog"] {
        background-color: #121212 !important;
        border: 1px solid #F59E0B !important;
    }
    div[data-testid="stDialog"] h1, div[data-testid="stDialog"] p, div[data-testid="stDialog"] label {
        color: white !important;
    }
    /* Memperjelas Radio Button (Absen & Lapkin) */
    div[role="radiogroup"] label {
        background-color: #262626 !important;
        padding: 10px !important;
        border-radius: 8px !important;
        margin-bottom: 5px !important;
        border: 1px solid #404040 !important;
    }
    div[role="radiogroup"] label p {
        color: #F59E0B !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONFIGURATION & DATABASE ---
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"
URL_LAPKIN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRAsm8AeVaDEUfGHvO95Q4IGSjmd7rDnK1Xt305f5UVrbr6V1TxURbVAnKLCfwv7My_NveJvbK439Wx/pub?output=csv"
SCRIPT_LAPKIN = "https://script.google.com/macros/s/AKfycbxRY5Tvp21WuX2VUMW43GmT8h_BcUUZkNog4CV5HKpThCEkC0YY61O0BF8m15Veqt6N/exec"

FORM_ID_PNS = "1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA"
FORM_ID_PPPK = "1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw"
E_NAMA, E_NIP, E_JABATAN = "entry.960346359", "entry.468881973", "entry.159009649"

DATABASE_INFO = {
    "Suwanto, SH., MH.": ["19720521 200912 1 001", "Sekretaris", "Sekretariat KPU Kab. Hulu Sungai Selatan", "-", "PNS", "Ketua KPU Kab. HSS", "-"],
    "Wawan Setiawan, SH": ["19860601 201012 1 004", "Kasubbag TP-Hupmas", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Ineke Setiyaningsih, S.Sos": ["19831003 200912 2 001", "Kasubbag Keuangan, Umum dan Logistik", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Farah Agustina Setiawati, SH": ["19840828 201012 2 003", "Kasubbag Hukum and SDM", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Rusma Ariati, SE": ["19840621 201101 2 013", "Kasubbag Perencanaan, Data dan Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Suwanto, SH., MH.", "19720521 200912 1 001"],
    "Suci Lestari, S.Ikom": ["19850108 201012 2 006", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Athaya Insyira Khairani, S.H": ["20010712202506 2 017", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Muhammad Ibnu Fahmi, S.H.": ["20010608202506 1 007", "Penyusun Materi Hukum Dan Perundang- Undangan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PNS", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Helmalina": ["19680318 199003 2 003", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ahmad Erwan Rifani, S.HI": ["19830829 200811 1 001", "Penelaah Teknis Kebijakan", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Najmi Hidayati": ["19850608 200701 2 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Muhammad Aldi Hudaifi, S.Kom": ["20010121202506 1 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Firda Aulia, S.Kom.": ["20020415202506 2 007", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PNS", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Jainal Abidin": ["19820712 200910 1 001", "Pengelola Layanan Operasional", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Syaiful Anwar": ["19741127 200710 1 001", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PNS", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Zainal Hilmi Yustan": ["19821025 200701 1 003", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Alfian Ridhani, S.Kom": ["19950903202506 1 005", "Penata Kelola Sistem Dan Teknologi Informasi", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PNS", "Rusma Ariati, SE", "19840621 201101 2 013"],

    "Saiful Fahmi, S.Pd": ["199506172025211036", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sulaiman": ["198411222024211010", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Teknis Penyelenggaraan Pemilu, Partisipasi dan Hubungan Masyarakat", "PPPK", "Wawan Setiawan, SH", "19860601 201012 1 004"],
    "Sya'bani Rona Baika": ["199202072024212044", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Basuki Rahmat": ["197705022024211007", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Saldoz Yedi": ["198008112025211019", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Mastoni Ridani": ["199106012025211018", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Suriadi": ["199803022025211005", "PENGELOLA UMUM OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Ami Aspihani": ["198204042025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Emaliani": ["198906222025212027", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "Nadianti": ["199906062025212036", "PENGADMINISTRASI PERKANTORAN", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Keuangan, Umum dan Logistik", "PPPK", "Ineke Setiyaningsih, S.Sos", "19831003 200912 2 001"],
    "M Satria Maipadly": ["198905262024211016", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Abdurrahman": ["198810122025211031", "OPERATOR LAYANAN OPERASIONAL", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Hukum dan Sumber Daya Manusia", "PPPK", "Farah Agustina Setiawati, SH", "19840828 201012 2 003"],
    "Apriadi Rakhman": ["198904222024211013", "PRANATA KOMPUTER AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"],
    "Muhammad Hafiz Rijani, S.KOM": ["199603212025211031", "PENATA KELOLA PEMILU AHLI PERTAMA", "Sekretariat KPU Kab. Hulu Sungai Selatan", "Sub Bagian Perencanaan, Data dan Informasi", "PPPK", "Rusma Ariati, SE", "19840621 201101 2 013"]
}

MASTER_PNS = [k for k, v in DATABASE_INFO.items() if v[4] == "PNS"]
MASTER_PPPK = [k for k, v in DATABASE_INFO.items() if v[4] == "PPPK"]

# --- 3. HELPERS ---
def get_clean_df(url):
    try:
        r = requests.get(f"{url}&cb={random.random()}", timeout=15)
        return pd.read_csv(StringIO(r.text)).dropna(how='all')
    except: return None

def clean_logic(name):
    return str(name).strip().lower().replace(",", "").replace(".", "").replace(" ", "")

# --- 4. DIALOGS ---
@st.dialog("Update Data")
def pop_update(nama):
    st.write(f"Pegawai: **{nama}**")
    tipe = st.radio("Pilih Kegiatan:", ["Absen", "Lapkin"])
    info = DATABASE_INFO[nama]
    if tipe == "Absen":
        if st.button("🚀 KIRIM ABSEN SEKARANG"):
            f_id = FORM_ID_PNS if info[4] == "PNS" else FORM_ID_PPPK
            payload = {E_NAMA: nama, E_NIP: info[0], E_JABATAN: info[1], "submit": "Submit"}
            try:
                requests.post(f"https://docs.google.com/forms/d/e/{f_id}/formResponse", data=payload, timeout=5)
                st.success("Terkirim!"); time.sleep(1.5); st.rerun()
            except: st.success("Selesai!"); time.sleep(1.5); st.rerun()
    else:
        st_fix = st.selectbox("Status:", ["Hadir", "Izin", "Sakit", "Tugas Luar", "Cuti"])
        h_kerja = st.text_area("Uraian Hasil Kerja:")
        if st.button("📝 SIMPAN LAPKIN"):
            payload = {"nama": nama, "nip": info[0], "jabatan": info[1], "status": st_fix, "hasil": h_kerja}
            requests.post(SCRIPT_LAPKIN, json=payload); st.success("Tersimpan!"); time.sleep(1); st.rerun()

@st.dialog("Advanced Rekap Excel", width="large")
def pop_rekap():
    st.markdown("### 📊 FILTER REKAP LENGKAP")
    c1, c2 = st.columns(2)
    with c1: r_bulan = st.selectbox("Pilih Bulan:", ["SEPANJANG TAHUN"] + LIST_BULAN)
    with c2: r_tahun = st.selectbox("Pilih Tahun:", ["2025", "2026", "2027"], index=1)
    c3, c4 = st.columns(2)
    with c3: r_kat = st.selectbox("Jenis Pegawai:", ["SEMUA PEGAWAI", "PNS", "PPPK"])
    with c4:
        if r_kat == "PNS": opts = ["-- Semua PNS --"] + MASTER_PNS
        elif r_kat == "PPPK": opts = ["-- Semua PPPK --"] + MASTER_PPPK
        else: opts = ["-- Semua Pegawai --"] + list(DATABASE_INFO.keys())
        r_nama = st.selectbox("Pilih Nama Spesifik:", opts)

    if st.button("📊 PROSES & DOWNLOAD EXCEL", use_container_width=True):
        df1, df2 = get_clean_df(URL_PNS), get_clean_df(URL_PPPK)
        if df1 is not None and df2 is not None:
            df = pd.concat([df1, df2], ignore_index=True)
            df['ts_str'] = df.iloc[:, 0].astype(str)
            df = df[df['ts_str'].str.contains(str(r_tahun))]
            if r_bulan != "SEPANJANG TAHUN":
                m_idx = f"{LIST_BULAN.index(r_bulan)+1:02d}"
                df = df[df['ts_str'].str.contains(f"/{m_idx}/") | df['ts_str'].str.contains(f"-{m_idx}-")]
            if "Semua" not in r_nama: df = df[df.iloc[:, 1] == r_nama]
            elif r_kat == "PNS": df = df[df.iloc[:, 1].isin(MASTER_PNS)]
            elif r_kat == "PPPK": df = df[df.iloc[:, 1].isin(MASTER_PPPK)]
            out = BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as writer: df.to_excel(writer, index=False)
            st.download_button("📥 DOWNLOAD REKAP", out.getvalue(), f"REKAP_{r_kat}_{r_bulan}.xlsx", use_container_width=True)

@st.dialog("Download Laporan Bulanan")
def pop_cetak():
    c_b = st.selectbox("Pilih Bulan Laporan:", LIST_BULAN, index=datetime.now(wita_tz).month-1)
    c_n = st.selectbox("Pilih Nama Pegawai:", list(DATABASE_INFO.keys()))
    if st.button("📊 GENERATE LAPKIN", use_container_width=True):
        df = get_clean_df(URL_LAPKIN)
        if df is not None:
            df_f = df[(df.iloc[:, 1] == c_n)].copy()
            if not df_f.empty:
                info = DATABASE_INFO[c_n]
                atasan_nama = info[5]
                if atasan_nama == "Suwanto, SH., MH.": j_atasan = "Sekretaris KPU Kab. Hulu Sungai Selatan"
                elif "Sekretaris" in info[1]: j_atasan = "Ketua KPU Kab. Hulu Sungai Selatan"
                else:
                    j_raw = DATABASE_INFO.get(atasan_nama, ["-", "Kepala Sub Bagian"])[1]
                    j_atasan = j_raw
                    if "Kasubbag" in j_raw or "TP-Hupmas" in j_raw:
                        if "TP-Hupmas" in j_raw: j_atasan = "Kepala Sub Bagian Teknis Penyelenggaraan Pemilu,\nPartisipasi dan Hubungan Masyarakat"
                        elif "Keuangan" in j_raw: j_atasan = "Kepala Sub Bagian Keuangan,\nUmum dan Logistik"
                        elif "Hukum" in j_raw: j_atasan = "Kepala Sub Bagian Hukum dan\nSumber Daya Manusia"
                        elif "Perencanaan" in j_raw: j_atasan = "Kepala Sub Bagian Perencanaan,\nData dan Informasi"

                hr_t = calendar.monthrange(datetime.now(wita_tz).year, LIST_BULAN.index(c_b)+1)[1]
                tgl_f = f"{hr_t} {c_b} {datetime.now(wita_tz).year}"
                out = BytesIO()
                with pd.ExcelWriter(out, engine='openpyxl') as writer:
                    header = [["LAPORAN BULANAN"], ["SEKRETARIAT KPU KABUPATEN HULU SUNGAI SELATAN"], [], ["Bulan", f": {c_b}"], ["Nama", f": {c_n}"], ["Jabatan", f": {info[1]}"], ["Unit Kerja", f": {info[2]}"], ["Sub Bagian", f": {info[3]}"], [], ["Hasil Kinerja", ":"], ["No", "Hari / Tanggal", "Uraian Kegiatan", "Hasil Kerja/Output", "Keterangan"]]
                    body = [[i+1, f"{pd.to_datetime(r.iloc[0], dayfirst=True).day} {LIST_BULAN[pd.to_datetime(r.iloc[0], dayfirst=True).month-1]} {pd.to_datetime(r.iloc[0], dayfirst=True).year}", f"Melaksanakan Pekerjaan sesuai Tupoksi pada {info[3]} di {info[2]}", r.iloc[5], "-"] for i, (_, r) in enumerate(df_f.iterrows())]
                    footer = [[], ["", "", "", f"Kandangan, {tgl_f}"], ["", "", "", "Atasan Langsung,"], ["", "", "", j_atasan], [], [], [], ["", "", "", atasan_nama], ["", "", "", f"NIP. {info[6]}"]]
                    pd.DataFrame(header).to_excel(writer, index=False, header=False, sheet_name="Laporan")
                    pd.DataFrame(body).to_excel(writer, startrow=11, index=False, header=False, sheet_name="Laporan")
                    pd.DataFrame(footer).to_excel(writer, startrow=11+len(body), index=False, header=False, sheet_name="Laporan")
                st.download_button("📥 DOWNLOAD", out.getvalue(), f"LAPKIN_{c_n}.xlsx", use_container_width=True)

# --- 5. MAIN UI ---
st.markdown('<div class="header-box">🏛️ MONITORING KPU HSS</div>', unsafe_allow_html=True)
st.markdown(f'<div class="clock-box">{datetime.now(wita_tz).strftime("%H:%M:%S WITA")}</div>', unsafe_allow_html=True)
_, mid, _ = st.columns([0.1, 5, 0.1])
with mid:
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a: 
        if st.button("🔄 REFRESH"): st.rerun()
    with col_b: pilih_tgl = st.date_input("Tgl", value=datetime.now(wita_tz).date(), label_visibility="collapsed")
    with col_c: 
        if st.button("📥 REKAP"): pop_rekap()
    with col_d: 
        if st.button("🖨️ DOWNLOAD"): pop_cetak()

st.write("---")
tab_all, tab_pns, tab_pppk = st.tabs(["🌎 SEMUA PEGAWAI", "👥 PNS", "👥 PPPK"])

def render_ui(urls, masters, tgl_target, tab_id):
    all_dfs = []
    for u in urls:
        df_t = get_clean_df(u)
        if df_t is not None: all_dfs.append(df_t)
    if not all_dfs: return
    df = pd.concat(all_dfs, ignore_index=True)
    d_f1, d_f2 = tgl_target.strftime('%d/%m/%Y'), tgl_target.strftime('%Y-%m-%d')
    log = {}
    for _, r in df.iterrows():
        ts = str(r.iloc[0])
        if d_f1 in ts or d_f2 in ts:
            n_raw = clean_logic(r.iloc[1])
            dt = pd.to_datetime(ts, errors='coerce')
            if pd.isna(dt): continue
            matched = next((m for m in masters if clean_logic(m) == n_raw), None)
            if matched:
                if matched not in log: log[matched] = {"m": dt.strftime("%H:%M"), "p": "--:--", "k": "HADIR" if dt.hour < 9 else "TERLAMBAT"}
                if dt.hour >= 15: log[matched]["p"] = dt.strftime("%H:%M")
    for i, p in enumerate(masters, 1):
        d = log.get(p, {"m": "--:--", "p": "--:--", "k": "ALPA"})
        st_cls = "status-hadir" if d['k'] == "HADIR" else "status-terlambat" if d['k'] == "TERLAMBAT" else "status-alpa"
        c_main, c_side = st.columns([8.5, 1.5])
        with c_main: st.markdown(f'<div class="employee-card"><div class="emp-name">{i}. {p}</div><div class="emp-time">M: <b>{d["m"]}</b></div><div class="emp-time">P: <b>{d["p"]}</b></div><div class="emp-status {st_cls}">{d["k"]}</div></div>', unsafe_allow_html=True)
        with c_side:
            if st.button("Update", key=f"btn_{p}_{tab_id}"): pop_update(p)

with tab_all: render_ui([URL_PNS, URL_PPPK], list(DATABASE_INFO.keys()), pilih_tgl, "all")
with tab_pns: render_ui([URL_PNS], MASTER_PNS, pilih_tgl, "pns")
with tab_pppk: render_ui([URL_PPPK], MASTER_PPPK, pilih_tgl, "pppk")
