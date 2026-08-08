import json
import re
import urllib.request

M3U_FILE = "boncuk"

def get_youtube_m3u8(youtube_url):
    """YouTube live sayfasından gizli hlsManifestUrl (.m3u8) adresini çeker."""
    try:
        req = urllib.request.Request(
            youtube_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
            }
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8')
            
            # YouTube HTML içerisindeki canlı m3u8 adresini yakala
            match = re.search(r'"hlsManifestUrl":"(https:[^"]+)"', html)
            if match:
                clean_url = match.group(1).replace('\\/', '/').replace('\\u0026', '&')
                return clean_url
            else:
                print(f"-> m3u8 deseni bulunamadı: {youtube_url}")
    except Exception as e:
        print(f"-> Bağlantı Hatası ({youtube_url}): {e}")
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

        # #EXTINF... tvg-id="Kanal" altındaki URL'yi yakalayan regex
        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        match = pattern.search(content)
        if match:
            print(f"-> Eşleşti, m3u8 çekiliyor...")
            live_url = get_youtube_m3u8(yt_url)

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
