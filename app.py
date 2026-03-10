import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import StringIO
import time

st.set_page_config(layout="wide")

# ================= URL =================

MASTER_URL = "ISI_LINK_MASTER_CSV"
ABSEN_URL = "ISI_LINK_ABSEN_CSV"

FORM_URL = "ISI_LINK_FORM_RESPONSE"
ENTRY_ID = "entry.123456789"


# ================= STYLE =================

st.markdown("""
<style>

.title{
text-align:center;
font-size:30px;
font-weight:bold;
}

.clock{
text-align:center;
font-size:42px;
color:#3fa7ff;
}

.card{
background:#111;
padding:15px;
border-radius:10px;
border:1px solid #333;
text-align:center;
}

.hadir{color:#2ecc71;font-weight:bold;}
.telat{color:#f1c40f;font-weight:bold;}
.alpa{color:#e74c3c;font-weight:bold;}

.stButton button{
border-radius:50%;
width:40px;
height:40px;
}

</style>
""",unsafe_allow_html=True)


# ================= HEADER =================

now=datetime.now()

st.markdown("<div class='title'>MONITORING ABSENSI KPU HSS</div>",unsafe_allow_html=True)

st.markdown(f"<div class='clock'>{now.strftime('%H:%M:%S')}</div>",unsafe_allow_html=True)

tanggal=st.date_input("Tanggal",now.date())


# ================= LOAD MASTER =================

def load_master():

    r=requests.get(MASTER_URL)

    df=pd.read_csv(StringIO(r.text))

    df.columns=df.columns.str.strip()

    return df


# ================= LOAD ABSEN =================

def load_absen():

    r=requests.get(ABSEN_URL)

    df=pd.read_csv(StringIO(r.text))

    df.columns=df.columns.str.strip()

    return df


# ================= KIRIM ABSEN =================

def kirim(nama):

    payload={ENTRY_ID:nama}

    try:

        requests.post(FORM_URL,data=payload)

        st.success("Absensi terkirim")

        time.sleep(1)

        st.rerun()

    except:

        st.error("Gagal mengirim")


# ================= PROSES DATA =================

def proses(master,absen):

    log={}

    batas=9

    if absen.empty:
        return log

    waktu_col=absen.columns[0]
    nama_col=absen.columns[1]

    for _,r in absen.iterrows():

        ts=pd.to_datetime(r[waktu_col],errors="coerce")

        if pd.isna(ts):
            continue

        if ts.date()!=tanggal:
            continue

        nama=str(r[nama_col]).strip()

        jam=ts.strftime("%H:%M")

        status="HDR" if ts.hour< batas else "TLT"

        log[nama]={
        "jam":jam,
        "status":status
        }

    return log


master=load_master()

absen=load_absen()

log=proses(master,absen)


# ================= STATISTIK =================

total=len(master)

hadir=sum(1 for n in master["Nama"] if n in log)

telat=sum(1 for n in master["Nama"] if n in log and log[n]["status"]=="TLT")

alpa=total-hadir

c1,c2,c3,c4=st.columns(4)

c1.markdown(f"<div class='card'><h2>{total}</h2>Total Pegawai</div>",unsafe_allow_html=True)

c2.markdown(f"<div class='card'><h2>{hadir}</h2>Hadir</div>",unsafe_allow_html=True)

c3.markdown(f"<div class='card'><h2>{telat}</h2>Telat</div>",unsafe_allow_html=True)

c4.markdown(f"<div class='card'><h2>{alpa}</h2>Alpa</div>",unsafe_allow_html=True)

st.divider()


# ================= HEADER TABEL =================

h1,h2,h3,h4,h5,h6=st.columns([1,4,3,4,2,2])

h1.write("No")

h2.write("Nama")

h3.write("NIP")

h4.write("Jabatan")

h5.write("Status")

h6.write("Aksi")


# ================= TABEL =================

for i,row in master.iterrows():

    nama=row["Nama"]

    nip=row["NIP"]

    jab=row["Jabatan"]

    data=log.get(nama,{"jam":"--","status":"ALPA"})

    warna={
    "HDR":"hadir",
    "TLT":"telat",
    "ALPA":"alpa"
    }[data["status"]]

    c1,c2,c3,c4,c5,c6=st.columns([1,4,3,4,2,2])

    c1.write(i+1)

    c2.write(nama)

    c3.write(nip)

    c4.write(jab)

    c5.markdown(f"<span class='{warna}'>{data['status']}</span>",unsafe_allow_html=True)

    with c6:

        b1,b2=st.columns(2)

        with b1:

            if st.button("P",key=f"p{i}"):

                kirim(nama)

        with b2:

            if st.button("S",key=f"s{i}"):

                kirim(nama)


# ================= DEBUG =================

with st.expander("DEBUG DATA"):

    st.write("MASTER PEGAWAI")

    st.dataframe(master)

    st.write("DATA ABSEN")

    st.dataframe(absen)
