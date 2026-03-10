import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
from io import StringIO

st.set_page_config(page_title="Absensi KPU HSS", layout="wide")

# ================= CSS =================
st.markdown("""
<style>

.centered {
    text-align:center;
}

.clock-style {
    font-size:60px;
    color:#3498db;
    font-weight:bold;
}

.row {
    border-bottom:1px solid #444;
    padding:8px 0;
}

.stButton button {
    width:50px;
    height:50px;
    border-radius:50%;
    font-weight:bold;
    font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# ================= MASTER DATA =================
MASTER_DATA = {
"PNS":[
"Suwanto, SH., MH.",
"Wawan Setiawan, SH",
"Ineke Setiyaningsih, S.Sos",
"Farah Agustina Setiawati, SH",
"Rusma Ariati, SE",
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
],

"PPPK":[
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
}

# ================= URL =================
URL_PNS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYD-AykhJVjxuA9m58Lm2V_cRkY0lJCU-tqRkC3KSIYapExZ_mjjUp7P0cPN65woxgP40cAFT0OQxB/pub?output=csv"
URL_PPPK = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSBqcP87DFbzstOyigKoUnn35yItImnsvxm_5F7oJLgeFmGVYjXXmTv7GpBWV6yEjkdwJkQ26yOVg_1/pub?output=csv"

FORM_PNS = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/formResponse"
FORM_PPPK = "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/formResponse"

# ================= TIME =================
wita_now = datetime.now() + timedelta(hours=8)
is_pagi = wita_now.hour < 11

# ================= HEADER =================
st.markdown("<h2 class='centered'>📊 MONITORING ABSENSI KPU HSS</h2>", unsafe_allow_html=True)
st.markdown(f"<div class='centered clock-style'>{wita_now.strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

tgl_pilihan = st.date_input("Tanggal", wita_now.date())

# ================= FETCH DATA =================
def fetch_data(url):

    try:

        res = requests.get(f"{url}&cache={random.random()}", timeout=10)

        df = pd.read_csv(StringIO(res.text))

        df.columns = df.columns.str.strip()

        return df

    except:

        return pd.DataFrame()

# ================= KIRIM ABSENSI =================
def kirim_data(url, nama, tipe):

    headers = {
        "User-Agent":"Mozilla/5.0",
        "Content-Type":"application/x-www-form-urlencoded"
    }

    payload = {
        "entry.960346359": nama
    }

    try:

        res = requests.post(url, data=payload, headers=headers)

        if res.status_code == 200:

            st.success(f"Absen {tipe} berhasil : {nama}")

            time.sleep(1)

            st.rerun()

        else:

            st.error("Gagal kirim ke Google Form")

    except Exception as e:

        st.error(e)

# ================= RENDER LIST =================
def render_list(df, master, form_url, prefix):

    batas_masuk = datetime.strptime("09:00","%H:%M").time()
    batas_pulang = datetime.strptime("16:00","%H:%M").time()

    log = {}

    if not df.empty:

        for _,r in df.iterrows():

            try:

                ts = pd.to_datetime(r.iloc[0], dayfirst=True)

                nama = str(r.iloc[1]).strip()

                if ts.date() == tgl_pilihan:

                    jam = ts.time()

                    if nama not in log:

                        status = "HDR" if jam <= batas_masuk else "TLT"

                        log[nama] = {
                        "m":jam.strftime("%H:%M"),
                        "p":"--",
                        "k":status
                        }

                    elif jam >= batas_pulang:

                        log[nama]["p"] = jam.strftime("%H:%M")

            except:
                pass

    # HEADER TABLE
    st.write("---")

    h1,h2,h3,h4,h5,h6 = st.columns([1,4,2,2,1,2])

    h1.write("No")
    h2.write("Nama")
    h3.write("Pagi")
    h4.write("Sore")
    h5.write("St")
    h6.write("Aksi")

    # ROW
    for i,p in enumerate(sorted(master),1):

        data = log.get(p,{
        "m":"--",
        "p":"--",
        "k":"ALPA"
        })

        warna = "green" if data["k"]=="HDR" else "orange" if data["k"]=="TLT" else "red"

        c1,c2,c3,c4,c5,c6 = st.columns([1,4,2,2,1,2])

        c1.write(i)

        c2.write(p.split(",")[0])

        c3.write(data["m"])

        c4.write(data["p"])

        c5.markdown(f":{warna}[**{data['k']}**]")

        with c6:

            b1,b2 = st.columns(2)

            with b1:

                if st.button("P", key=f"p_{prefix}_{i}", disabled=not is_pagi):

                    kirim_data(form_url, p, "PAGI")

            with b2:

                if st.button("S", key=f"s_{prefix}_{i}", disabled=is_pagi):

                    kirim_data(form_url, p, "SORE")

# ================= TAB =================
tab1,tab2 = st.tabs(["PNS","PPPK"])

with tab1:

    df = fetch_data(URL_PNS)

    render_list(df, MASTER_DATA["PNS"], FORM_PNS, "pns")

with tab2:

    df = fetch_data(URL_PPPK)

    render_list(df, MASTER_DATA["PPPK"], FORM_PPPK, "pppk")
