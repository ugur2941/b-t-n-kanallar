import requests
import json

def get_vavoo_token():
    url = "https://vavoo.to"
    headers = {"User-Agent": "VAVOO/2.6", "Content-Type": "application/json"}
    try:
        response = requests.post(url, json={"id": "", "ver": "2.6"}, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("signed") or response.json().get("token")
    except:
        return None

token = get_vavoo_token()
if token:
    # Örnek olarak test ettiğiniz kanal ID'sini listeye ekliyoruz
    # İleride buraya istediğiniz kadar kanal ID'si ekleyebilirsiniz
    kanallar = [
        {"adi": "Vavoo Test Kanali", "id": "22284968562a623d1b95b4"}
    ]
    
    # M3U dosyasını oluşturuyoruz
    m3u_icerik = "#EXTM3U\n"
    for kanal in kanallar:
        m3u_icerik += f"#EXTINF:-1, {kanal['adi']}\n"
        # Sizin istediğiniz kusursuz format: https://vavoo.to
        m3u_icerik += f"https://vavoo.to{kanal['id']}.m3u8?key={token}\n"
        
    with open("vavoo_listem.m3u", "w", encoding="utf-8") as f:
        f.write(m3u_icerik)
    print("M3U Listesi taze token ile basariyla guncellendi!")
