def kirim_absen_silent(nama, is_pns):
    view_url = "https://docs.google.com/forms/d/e/1FAIpQLSdfwUrcxoTer6M2NEMOpxoFYF8e9lBe5reG7rF1ZQIdtjRwzA/viewform" if is_pns else "https://docs.google.com/forms/d/e/1FAIpQLSe4pgHjDzZB9OTgbq7XNw5SWTNIo0AjTnnVUukd13e9BgkNPw/viewform"
    post_url = view_url.replace("/viewform", "/formResponse")
    info = DATABASE_INFO.get(nama)
    
    # Payload dengan data tambahan agar Google tidak curiga
    payload = {
        "entry.960346359": nama,
        "entry.468881973": info[0],
        "entry.159009649": info[1],
        "fvv": "1",
        "draftResponse": "[]",
        "pageHistory": "0"
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0"
    }

    try:
        # Gunakan timeout lebih lama karena server Cloud kadang lambat
        r = requests.post(post_url, data=payload, headers=headers, timeout=20)
        
        # DEBUG: Cetak status ke log (bisa dilihat di tombol 'Manage App' Streamlit)
        print(f"Status: {r.status_code} untuk nama {nama}")
        
        # Google Form sukses biasanya kasih status 200
        if r.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False
