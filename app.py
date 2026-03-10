import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from io import StringIO
import random
import time

st.set_page_config(page_title="Monitoring Absensi", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>

.title{
text-align:center;
font-size:32px;
font-weight:bold;
}

.clock{
text-align:center;
font-size:50px;
color:#3498db;
}

.stat{
background:#111;
padding:20px;
border-radius:10px;
border:1px solid #333;
text-align:center;
}

.stat-number{
font-size:28px;
font-weight:bold;
}

.badge-hadir{color:#2ecc71;font-weight:bold;}
.badge-telat{color:#f39c12;font-weight:bold;}
.badge-alpa{color:#e74c3c;font-weight:bold;}

.stButton button{
width:42px;
height:42px;
border-radius:50%;
font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ================= MASTER DATA =================
MASTER = [
"Suwanto","Wawan Setiawan","Ineke Setiyaningsih",
"Farah Agustina Setiawati","Rusma Ariati","Helmalina",
"Ahmad Erwan Rifani","Syaiful Anwar","Zainal Hilmi Yustan",
"Najmi Hidayati","Jainal Abidin","Suci Lestari",
"Athaya Insyira Khairani","Muhammad Ibnu Fahmi",
"Alfian Ridhani","Muhammad Aldi Hudaifi","Firda Aulia",
"Sya'bani Rona Baika","Apriadi Rakhman","M Satria Maipadly",
"Basuki Rahmat","Sulaiman","Saldoz Yedi","Mastoni Ridani",
"Suriadi","Ami Aspihani","Abdurrahman","Emaliani",
"Muhammad Hafiz Rijani","Saiful Fahmi","Nadianti"
]

# ================= URL =================
CSV_URL = "URL_CSV_GOOGLE_SHEET"
FORM_URL = "URL_FORM"
ENTRY_ID = "entry.960346359"

# ================= TIME =================
now = datetime.now() + timedelta(hours=8)

st.markdown("<div class='title'>MONITORING ABSENSI KPU HSS</div>", unsafe_allow_html=True)

st.markdown(
f"<div class='clock'>{now.strftime('%H:%M:%S')}</div>",
unsafe_allow_html=True
)

tanggal = st.date_input("Tanggal", now.date())

if st.button("🔍 CEK DATA ABSENSI"):
    st.rerun()

# ================= FETCH DATA =================
def fetch_data():

    try:

        r = requests.get(f"{CSV_URL}&cache={random.random()}")

        df = pd.read_csv(StringIO(r.text))

        df.columns = df.columns.str.strip()

        return df

    except:

        return pd.DataFrame()

# ================= KIRIM ABSEN =================
def kirim_absen(nama):

    payload = {ENTRY_ID: nama}

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.post(FORM_URL, data=payload, headers=headers)

    if r.status_code == 200:

        st.toast("Absensi berhasil")

        time.sleep(1)

        st.rerun()

    else:

        st.error("Gagal kirim absensi")

# ================= PROSES DATA =================
def proses(df):

    batas = datetime.strptime("09:00", "%H:%M").time()

    log = {}

    if df.empty:
        return log

    waktu_col = df.columns[0]
    nama_col = df.columns[1]

    for _, r in df.iterrows():

        try:

            ts = pd.to_datetime(r[waktu_col], errors="coerce")

            if pd.isna(ts):
                continue

            nama = str(r[nama_col]).strip()

            if ts.date() == tanggal:

                jam = ts.time()

                status = "HDR" if jam <= batas else "TLT"

                if nama not in log:

                    log[nama] = {
                        "masuk": jam.strftime("%H:%M"),
                        "pulang": "--",
                        "status": status
                    }

        except:
            pass

    return log

df = fetch_data()

# DEBUG DATA
with st.expander("DEBUG DATA GOOGLE SHEET"):
    st.dataframe(df)

log = proses(df)

# ================= STATISTIK =================
total = len(MASTER)

hadir = sum(1 for n in MASTER if n in log and log[n]["status"] == "HDR")

telat = sum(1 for n in MASTER if n in log and log[n]["status"] == "TLT")

alpa = total - hadir - telat

c1, c2, c3, c4 = st.columns(4)

c1.markdown(f"<div class='stat'><div class='stat-number'>{total}</div>Total Pegawai</div>", unsafe_allow_html=True)
c2.markdown(f"<div class='stat'><div class='stat-number'>{hadir}</div>Hadir</div>", unsafe_allow_html=True)
c3.markdown(f"<div class='stat'><div class='stat-number'>{telat}</div>Telat</div>", unsafe_allow_html=True)
c4.markdown(f"<div class='stat'><div class='stat-number'>{alpa}</div>Alpa</div>", unsafe_allow_html=True)

st.write("")

# ================= HEADER =================
h1,h2,h3,h4,h5,h6 = st.columns([1,4,2,2,2,2])

h1.write("No")
h2.write("Nama")
h3.write("Masuk")
h4.write("Pulang")
h5.write("Status")
h6.write("Aksi")

# ================= ROW =================
for i, nama in enumerate(MASTER, 1):

    data = log.get(nama, {
        "masuk": "--",
        "pulang": "--",
        "status": "ALPA"
    })

    warna = {
        "HDR": "badge-hadir",
        "TLT": "badge-telat",
        "ALPA": "badge-alpa"
    }[data["status"]]

    c1,c2,c3,c4,c5,c6 = st.columns([1,4,2,2,2,2])

    c1.write(i)
    c2.write(nama)
    c3.write(data["masuk"])
    c4.write(data["pulang"])

    c5.markdown(
        f"<span class='{warna}'>{data['status']}</span>",
        unsafe_allow_html=True
    )

    with c6:

        b1,b2 = st.columns(2)

        with b1:
            if st.button("P", key=f"p{i}"):
                kirim_absen(nama)

        with b2:
            if st.button("S", key=f"s{i}"):
                kirim_absen(nama)
