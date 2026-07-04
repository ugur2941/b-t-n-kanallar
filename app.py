from flask import Flask, redirect, jsonify
import requests

app = Flask(__name__)

def get_vavoo_token():
    url = "https://vavoo.to"
    
    # Vavoo'nun güncel bot engelleme sistemini aşmak için genişletilmiş başlıklar
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://vavoo.to",
        "Referer": "https://vavoo.to",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    # Sunucunun boş istekleri reddetmemesi için standart sürüm parametreleri
    payload = {"id": "", "ver": "2.6"} 
    
    try:
        # Doğrulama oturumu simüle etmek için session kullanıyoruz
        session = requests.Session()
        response = session.post(url, json=payload, headers=headers, timeout=12)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("signed") or data.get("token")
            if token:
                return token
        print(f"Hata Kodu: {response.status_code} - Yanit: {response.text}")
    except Exception as e:
        print(f"Baglanti Hatasi: {e}")
    return None

@app.route('/vavoo-iptv/play/<channel_id>')
def play_channel(channel_id):
    token = get_vavoo_token()
    if token:
        stream_url = f"https://vavoo.tolive/{channel_id}.m3u8?key={token}"
        return redirect(stream_url)
    return jsonify({
        "error": "Token alinamadi", 
        "status": "Vavoo guvenlik duvari sunucu IP adresini engelliyor olabilir."
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

