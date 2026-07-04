from flask import Flask, redirect, request, jsonify
import requests

app = Flask(__name__)

def get_vavoo_token():
    url = "https://vavoo.to"
    headers = {
        "User-Agent": "VAVOO/2.6",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://vavoo.to",
        "Referer": "https://vavoo.to"
    }
    payload = {"id": "", "ver": "2.6"}
    
    proxy_urls = [
        "https://proxyscrape.com",
        "https://proxy-list.download"
    ]
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("signed") or data.get("token")
    except:
        pass

    for p_url in proxy_urls:
        try:
            proxies_list = requests.get(p_url, timeout=4).text.split('\r\n')
            for proxy in proxies_list[:5]:
                if proxy:
                    try:
                        px = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                        response = requests.post(url, json=payload, headers=headers, proxies=px, timeout=4)
                        if response.status_code == 200:
                            data = response.json()
                            token = data.get("signed") or data.get("token")
                            if token:
                                return token
                    except:
                        continue
        except:
            continue
    return None

# CATCH-ALL: Gelen her türlü uzun, kısa veya hatalı uzantılı isteği 404 VERMEDEN yakalar!
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    # Linkin sonundaki o uzun kanal ID'sini (hash) cımbızla çekiyoruz
    parts = path.split('/')
    raw_id = parts[-1] if parts else ""
    clean_id = raw_id.replace('.m3u8', '').split('?')[0]
    
    if not clean_id or len(clean_id) < 10:
        return jsonify({"error": "Gecersiz veya Eksik Kanal ID"}), 400

    token = get_vavoo_token()
    
    if token:
        # Doğru eğik çizgili ve taze şifreli resmi video akış linki (vavoo.to/live/)
        return redirect(f"https://vavoo.tolive/{clean_id}.m3u8?key={token}")
    
    # Şifre alınamazsa bile oynatıcının şansını denemesi için ham linke fırlatır
    return redirect(f"https://vavoo.tolive/{clean_id}.m3u8")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
