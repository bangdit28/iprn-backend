import os
import re
import xlsxwriter
import requests
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from io import BytesIO

app = Flask(__name__)
CORS(app)

# MASUKKAN DATA DARI SUPABASE TADI
SUPABASE_URL = "https://ocurwurtpayzqqgfdlgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9jdXJ3dXJ0cGF5enFxZ2ZkbGdrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA0NDMzMDYsImV4cCI6MjA4NjAxOTMwNn0.2YWZc4LJzEXhCwuSPTo00fCfm7jawEmihVcwKFIYIiQ"

def extract_uid(cookie_string):
    match = re.search(r"c_user=(\d+)", cookie_string)
    return match.group(1) if match else "UID_TIDAK_ADA"

@app.route('/save-cookie', methods=['POST'])
def save_cookie():
    data = request.json
    user_id = str(data.get('user_id'))
    raw_cookie = data.get('cookie', '').strip()
    password = data.get('password', 'tasik321')

    if not raw_cookie: return jsonify({"error": "Kosong"}), 400

    uid = extract_uid(raw_cookie)
    formatted = f"{uid}|{password}|{raw_cookie}"

    # SIMPAN KE SUPABASE (DATABASE ABADI)
    payload = {
        "user_id": user_id, "uid": uid, "password": password,
        "raw_cookie": raw_cookie, "formatted": formatted
    }
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    requests.post(f"{SUPABASE_URL}/rest/v1/cookies_fb", json=payload, headers=headers)

    # Ambil total terbaru dari DB
    r = requests.get(f"{SUPABASE_URL}/rest/v1/cookies_fb?user_id=eq.{user_id}&select=count", headers=headers)
    total = r.json()[0]['count'] if r.ok else 0

    return jsonify({"status": "success", "total": total})

@app.route('/get-status', methods=['GET'])
def get_status():
    user_id = request.args.get('user_id')
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = requests.get(f"{SUPABASE_URL}/rest/v1/cookies_fb?user_id=eq.{user_id}&select=count", headers=headers)
    total = r.json()[0]['count'] if r.ok else 0
    return jsonify({"total": total})

@app.route('/clear-data', methods=['POST'])
def clear_data():
    user_id = request.json.get('user_id')
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    requests.delete(f"{SUPABASE_URL}/rest/v1/cookies_fb?user_id=eq.{user_id}", headers=headers)
    return jsonify({"status": "success", "total": 0})

@app.route('/download-excel', methods=['GET'])
def download_excel():
    user_id = request.args.get('user_id')
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    r = requests.get(f"{SUPABASE_URL}/rest/v1/cookies_fb?user_id=eq.{user_id}&select=uid,password,formatted", headers=headers)
    data = r.json()

    if not data: return "Data kosong", 400
    
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet()
    for col, h in enumerate(["UID", "Password", "Formatted"]): sheet.write(0, col, h)
    for row, item in enumerate(data, 1):
        sheet.write(row, 0, item['uid'])
        sheet.write(row, 1, item['password'])
        sheet.write(row, 2, item['formatted'])
    workbook.close()
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='cookies.xlsx')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
