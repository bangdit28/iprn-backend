import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 1. PASTIKAN COOKIE INI BARU (Ambil dari Inspect Element -> Network -> Cookie)
COOKIE_DATA = "PHPSESSID=u3ft88fp5slu1m761fsvd1ev75" 

def get_facebook_codes():
    # URL sesuai screenshot kamu
    url = "https://calltimepanel.com/yeni/TestSMS/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Cookie": COOKIE_DATA
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=15)
        # Jika diarahkan ke halaman login, berarti cookie mati
        if "login" in r.url.lower():
            return [{"range_sender": "ERROR", "code": "COOKIE MATI", "full_text": "Silahkan update cookie di app.py", "time": "now"}]

        soup = BeautifulSoup(r.text, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return []

        rows = table.find_all('tr')[1:] # Lewati header
        results = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                sender = cols[1].text.strip()
                receiver = cols[2].text.strip()
                sms_text = cols[3].text.strip()
                time = cols[4].text.strip()
                
                # Logika: Cek di teks SMS ATAU di nama Sender
                is_fb = "facebook" in sms_text.lower() or "facebook" in sender.lower()
                
                if is_fb:
                    # Cari angka 5 digit
                    match = re.search(r'(\d{5})', sms_text)
                    code = match.group(1) if match else "???"
                    
                    results.append({
                        "range_sender": sender,
                        "target": receiver,
                        "code": code,
                        "full_text": sms_text,
                        "time": time
                    })
        return results
    except Exception as e:
        return [{"range_sender": "SYSTEM ERROR", "code": "ERR", "full_text": str(e), "time": "now"}]

@app.route('/get-fb')
def get_fb():
    data = get_facebook_codes()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000) # Pastikan port 8000 sesuai Koyeb
