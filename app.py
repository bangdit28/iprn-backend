import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MASUKKAN COOKIE YANG TADI KAMU AMBIL DI FASE 1
COOKIE_DATA = "session_id=xxxxxxxxxxxxxxx; other_cookie=yyyyyy"

def scrape_panel():
    url = "https://calltimepanel.com/dashboard" # Sesuaikan URL dashboard/stats
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": COOKIE_DATA
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # LOGIKA SCRAPING: Ini harus disesuaikan dengan isi web CallTimePanel
        # Ini contoh dummy:
        data_dummy = [
            {"range": "+235 (Chad)", "hits": 150, "payout": "$0.10"},
            {"range": "+241 (Gabon)", "hits": 10, "payout": "$0.08"},
            {"range": "+371 (Latvia)", "hits": 500, "payout": "$0.12"}
        ]
        return data_dummy
    except:
        return []

@app.route('/data')
def get_data():
    return jsonify(scrape_panel())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
