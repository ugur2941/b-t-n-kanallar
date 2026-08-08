import json
import re
import urllib.request

M3U_FILE = "boncuk"

def get_m3u8_via_api(youtube_url):
    """
    YouTube IP engellerine takılmamak için alternatif Invidious/Piped API 
    uç noktalarını kullanarak canlı m3u8 adresini çeker.
    """
    match = re.search(r'@([^/]+)', youtube_url)
    if not match:
        return None
    channel_handle = match.group(1)

    # YouTube IP engellerini aşan kamuya açık API uçları
    instances = [
        f"https://api.piped.private.coffee/channel/{channel_handle}",
        f"https://pipedapi.kavin.rocks/channel/{channel_handle}",
        f"https://inv.tux.pizza/api/v1/channels/{channel_handle}"
    ]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

    for api_url in instances:
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                html_or_json = response.read().decode('utf-8')
                
                # Yanıt içerisindeki m3u8 adresini arayan düzeltilmiş Regex
                m3u8_match = re.search(r'https?://[^\s"<>\'"]+?\.m3u8[^\s"<>\'"]*', html_or_json)
                if m3u8_match:
                    return m3u8_match.group(0)
        except Exception:
            continue

    # Alternatif: Doğrudan HTML scraping
    scrape_url = f"https://yt.artemislena.eu/live/{channel_handle}"
    try:
        req = urllib.request.Request(scrape_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            m3u8_match = re.search(r'https?://[^\s"<>\'"]+?\.m3u8[^\s"<>\'"]*', html)
            if m3u8_match:
                return m3u8_match.group(0)
    except Exception:
        pass

    return None

def main():
    print("--- 1. youtube.json Okunuyor ---")
    try:
        with open('youtube.json', 'r', encoding='utf-8') as f:
            yt_channels = json.load(f)
    except Exception as e:
        print(f"HATA: youtube.json okunamadı -> {e}")
        return

    print("--- 2. boncuk Dosyası Okunuyor ---")
    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"HATA: '{M3U_FILE}' okunamadı -> {e}")
        return

    updated = False

    print("--- 3. Güncelleme Başlıyor ---")
    for channel in yt_channels:
        tvg_id = channel.get('tvg_id', '').strip()
        yt_url = channel.get('youtube_url', '').strip()

        print(f"\n[İşleniyor]: '{tvg_id}'")

        # #EXTINF... tvg-id="Kanal" altındaki URL satırını yakalar
        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        if pattern.search(content):
            print(f"-> Eşleşti, m3u8 adresi çekiliyor...")
            live_url = get_m3u8_via_api(yt_url)

            if live_url:
                content = pattern.sub(r'\1' + live_url, content)
                print(f"-> BAŞARILI: {tvg_id} linki güncellendi!")
                updated = True
            else:
                print(f"-> HATA: {tvg_id} için canlı link alınamadı.")
        else:
            print(f"-> BULUNAMADI: '{tvg_id}'")

    if updated:
        with open(M3U_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n--- 'boncuk' DOSYASI BAŞARIYLA GÜNCELLENDİ VE KAYDEDİLDİ ---")
    else:
        print("\n--- HİÇBİR DEĞİŞİKLİK YAPILMADI ---")

if __name__ == "__main__":
    main()
