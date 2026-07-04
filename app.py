from flask import Flask, redirect, jsonify
import requests

app = Flask(__name__)

def get_vavoo_token():
    # Vavoo'nun resmi token başlatma adresi
    url = "https://vavoo.to"
    headers = {
        "User-Agent": "VAVOO/2.6",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {"id": "", "ver": "2.6"} 
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Sunucudan gelen imzalı anahtarı alıyoruz
            return data.get("signed") or data.get("token")
    except Exception as e:
        return None
    return None

# Sizin kullandığınız link yapısına (play/kanal_id) uyumlu endpoint
@app.route('/vavoo-iptv/play/<channel_id>')
def play_channel(channel_id):
    token = get_vavoo_token()
    if token:
        # kool.to yerine doğrudan resmi Vavoo sunucusundan taze tokenlı temiz linki üretiyoruz
        stream_url = f"https://vavoo.to{channel_id}.m3u8?key={token}"
        
        # Oynatıcınızı reklamsız ve kesintisiz linke yönlendiriyoruz
        return redirect(stream_url)
    return jsonify({"error": "Token alinamadi"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
