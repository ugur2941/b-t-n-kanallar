from flask import Flask, redirect, jsonify
import requests

app = Flask(__name__)

def get_vavoo_token():
    url = "https://vavoo.to"
    headers = {
        "User-Agent": "VAVOO/2.6",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {"id": "", "ver": "2.6"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("signed") or data.get("token")
    except:
        return None
    return None

@app.route('/vavoo-iptv/play/<channel_id>')
@app.route('/vavoo/<channel_id>')
def play_channel(channel_id):
    clean_id = channel_id.replace('.m3u8', '')
    token = get_vavoo_token()
    
    if token:
        # İSTEDİĞİNİZ KUSURSUZ FORMAT: https://vavoo.to
        return redirect(f"https://vavoo.to{clean_id}.m3u8?key={token}")
    
    return redirect(f"https://vavoo.to{clean_id}.m3u8")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)




