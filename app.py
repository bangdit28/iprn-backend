import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# GANTI DENGAN COOKIE LOGIN KAMU (Cek di FASE 1 cara ambilnya)
COOKIE_DATA = "PHPSESSID=u3ft88fp5slu1m761fsvd1ev75"

def get_facebook_codes():
    url = "https://calltimepanel.com/yeni/TestSMS/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie": COOKIE_DATA
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Cari tabel di halaman tersebut
        table = soup.find('table')
        rows = table.find_all('tr')[1:] # Lewati header tabel
        
        results = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                sender = cols[1].text.strip()    # Kolom Sender
                receiver = cols[2].text.strip()  # Kolom Receiver
                sms_text = cols[3].text.strip()  # Kolom Text (Isi SMS)
                time = cols[4].text.strip()      # Kolom Sent Date
                
                # LOGIKA: Cek apakah ada kata "Facebook" (abaikan besar kecil huruf)
                if "facebook" in sms_text.lower():
                    # Ambil angka 5 digit dari SMS
                    match = re.search(r'(\d{5})', sms_text)
                    if match:
                        code = match.group(1)
                        results.append({
                            "range_sender": sender,
                            "target": receiver,
                            "code": code,
                            "full_text": sms_text,
                            "time": time
                        })
        return results
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.route('/get-fb')
def get_fb():
    data = get_facebook_codes()
    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
