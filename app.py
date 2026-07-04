from flask import Flask, redirect, jsonify
import requests

app = Flask(__name__)

def get_vavoo_token():
    url = "https://vavoo.to"
    headers = {
        "User-Agent": "VAVOO/2.6",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://vavoo.to",
        "Referer": "https://vavoo.to/"
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

# Hem eski uzun linkleri hem yeni kısa linkleri yakalar
@app.route('/vavoo-iptv/play/<channel_id>')
@app.route('/vavoo/<channel_id>')
def play_channel(channel_id):
    clean_id = channel_id.replace('.m3u8', '')
    token = get_vavoo_token()
    
    if token:
        # KONTROL EDİLDİ: Eğik çizgi eklendi -> vavoo.to/live
        stream_url = f"https://vavoo.to/live/{clean_id}.m3u8?key={token}"
        return redirect(stream_url)
    
    # KONTROL EDİLDİ: Eğik çizgi eklendi -> vavoo.to/live
    return redirect(f"https://vavoo.to/live/{clean_id}.m3u8")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


