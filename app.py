import os
import re
import xlsxwriter
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)
CORS(app)

user_storage = {}

def extract_uid(cookie_string):
    match = re.search(r"c_user=(\d+)", cookie_string)
    return match.group(1) if match else "UID_TIDAK_ADA"

@app.route('/')
def home():
    return "Backend Aktif & Cepat!"

@app.route('/save-cookie', methods=['POST'])
def save_cookie():
    data = request.json
    user_id = str(data.get('user_id', 'unknown'))
    raw_cookie = data.get('cookie', '').strip()
    password = data.get('password', 'tasik321')

    if not raw_cookie:
        return jsonify({"status": "error", "message": "Kosong"}), 400

    if user_id not in user_storage:
        user_storage[user_id] = []

    uid = extract_uid(raw_cookie)
    formatted_string = f"{uid}|{password}|{raw_cookie}"
    
    entry = {
        "uid": uid,
        "password": password,
        "cookie": raw_cookie,
        "formatted": formatted_string
    }
    
    user_storage[user_id].append(entry)
    # Langsung kembalikan total terbaru biar cepat
    return jsonify({
        "status": "success", 
        "total": len(user_storage[user_id])
    })

@app.route('/get-status', methods=['GET'])
def get_status():
    user_id = str(request.args.get('user_id', ''))
    count = len(user_storage.get(user_id, []))
    return jsonify({"total": count})

@app.route('/clear-data', methods=['POST'])
def clear_data():
    data = request.json
    user_id = str(data.get('user_id', ''))
    if user_id in user_storage:
        user_storage[user_id] = [] # Kosongkan list milik user tersebut
    return jsonify({"status": "success", "total": 0})

@app.route('/download-excel', methods=['GET'])
def download_excel():
    user_id = str(request.args.get('user_id', ''))
    data = user_storage.get(user_id, [])

    if not data:
        return "Data kosong!", 400
    
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet()
    headers = ["UID", "Password", "Formatted (Full)"]
    for col, header in enumerate(headers):
        sheet.write(0, col, header)
    for row, item in enumerate(data, start=1):
        sheet.write(row, 0, item['uid'])
        sheet.write(row, 1, item['password'])
        sheet.write(row, 2, item['formatted'])
    workbook.close()
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=f'cookies_{user_id}.xlsx')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
