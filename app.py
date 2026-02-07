import os
import re
import xlsxwriter
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Database sementara di RAM
storage = []

def extract_uid(cookie_string):
    match = re.search(r"c_user=(\d+)", cookie_string)
    return match.group(1) if match else "UID_TIDAK_ADA"

@app.route('/')
def home():
    return "Backend Aktif!"

@app.route('/save-cookie', methods=['POST'])
def save_cookie():
    data = request.json
    raw_cookie = data.get('cookie', '')
    password = data.get('password', 'tasik321')

    if not raw_cookie:
        return jsonify({"status": "error"}), 400

    uid = extract_uid(raw_cookie)
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

@app.route('/download-excel', methods=['GET'])
def download_excel():
    if not storage:
        return "Data masih kosong, silakan input dulu di bot!", 400
    
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet()

    # Header
    headers = ["UID", "Password", "Formatted (Full)"]
    for col, header in enumerate(headers):
        sheet.write(0, col, header)

    # Isi Data
    for row, item in enumerate(storage, start=1):
        sheet.write(row, 0, item['uid'])
        sheet.write(row, 1, item['password'])
        sheet.write(row, 2, item['formatted'])

    workbook.close()
    output.seek(0)
    
    return send_file(
        output, 
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True, 
        download_name='cookies_fb.xlsx'
    )

if __name__ == "__main__":
    # Koyeb menggunakan port 8000 secara default
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
