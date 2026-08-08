import json
import re
import urllib.request

M3U_FILE = "boncuk"

def get_m3u8_via_invidious(youtube_url):
    """
    YouTube IP engellerini aşmak için açık kaynak API ucu üzerinden
    canlı yayın .m3u8 bağlantısını çeker.
    """
    # URL'den kanal adını ayıkla (örn: SZCTVKanal)
    match = re.search(r'@([^/]+)', youtube_url)
    if not match:
        return None
    channel_handle = match.group(1)

    # YouTube IP engellerini aşmak için güvenilir kamuya açık API uçları
    api_instances = [
        f"https://inv.tux.pizza/api/v1/channels/symbolpress/{channel_handle}",
        f"https://invidious.drgns.space/api/v1/channels/symbolpress/{channel_handle}",
        f"https://vid.puffyan.us/api/v1/channels/symbolpress/{channel_handle}"
    ]

    # Doğrudan canlı yayının m3u8 manifest adresini HTML içerisinden yedek yöntemle arama
    scrape_urls = [
        f"https://yt.artemislena.eu/live/{channel_handle}",
        f"https://invidious.no-boomer.cafe/live/{channel_handle}"
    ]

    # Yöntem 1: Doğrudan alternatif HTML canlı yayın akışından m3u8 çekme
    for url in scrape_urls:
        try:
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                m3u8_match = re.search(r'(https?://[^\s"'<>]+?\.m3u8[^\s"'<>]*?)', html)
                if m3u8_match:
                    return m3u8_match.group(1)
        except Exception:
            continue

    # Yöntem 2: Invidious API üzerinden video id bulup m3u8 türetme
    for api_url in api_instances:
        try:
            req = urllib.request.Request(
                f"https://invidious.nerdvpn.de/api/v1/channels/{channel_handle}/live",
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if 'videoId' in data:
                    video_id = data['videoId']
                    # HLS manifest adresini getir
                    manifest_url = f"https://invidious.nerdvpn.de/api/v1/manifest/hls/{video_id}"
                    return manifest_url
        except Exception:
            continue

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

        # #EXTINF satırından sonra gelen HTTP linkini yakala
        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        if pattern.search(content):
            print(f"-> Eşleşti, m3u8 adresi çekiliyor...")
            live_url = get_m3u8_via_invidious(yt_url)

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
