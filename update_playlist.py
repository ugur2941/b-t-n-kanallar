import json
import re
import urllib.request

M3U_FILE = "boncuk"

def get_live_m3u8(youtube_url):
    """
    YouTube canlı yayın adresinden m3u8 linkini çekmek için
    mobil tarayıcı ve alternatif API katmanlarını kullanır.
    """
    # 1. YÖNTEM: Mobil iOS / Safari User-Agent (YouTube engeline takılmaz)
    mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Accept-Language': 'tr-TR,tr;q=0.9'
    }

    try:
        req = urllib.request.Request(youtube_url, headers=mobile_headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode('utf-8')
            
            # M3U8 linkini HTML içinden yakala
            match = re.search(r'"hlsManifestUrl":"(https:[^"]+)"', html)
            if match:
                return match.group(1).replace('\\/', '/').replace('\\u0026', '&')
    except Exception as e:
        print(f"   [1. Yöntem Başarısız]: Direct Mobil Request -> {e}")

    # 2. YÖNTEM: Kanal adı üzerinden Piped / Invidious API
    handle_match = re.search(r'@([^/]+)', youtube_url)
    if handle_match:
        handle = handle_match.group(1)
        api_urls = [
            f"https://pipedapi.kavin.rocks/channel/{handle}",
            f"https://api.piped.private.coffee/channel/{handle}",
            f"https://inv.tux.pizza/api/v1/channels/{handle}"
        ]

        for api in api_urls:
            try:
                req = urllib.request.Request(api, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=8) as response:
                    data_str = response.read().decode('utf-8')
                    m3u8_match = re.search(r'https?://[^\s"<>\']+\.m3u8[^\s"<>\']*', data_str)
                    if m3u8_match:
                        return m3u8_match.group(0)
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

    print("--- 3. Güncelleme İşlemi Başlıyor ---")
    for channel in yt_channels:
        tvg_id = channel.get('tvg_id', '').strip()
        yt_url = channel.get('youtube_url', '').strip()

        print(f"\n[Kanal Aranıyor]: '{tvg_id}' ({yt_url})")

        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        if pattern.search(content):
            print(f" -> Eşleşti, canlı link çekiliyor...")
            live_url = get_live_m3u8(yt_url)

            if live_url:
                content = pattern.sub(r'\1' + live_url, content)
                print(f" -> BAŞARILI: {tvg_id} linki güncellendi!")
                print(f"    Yeni Link: {live_url[:65]}...")
                updated = True
            else:
                print(f" -> HATA: {tvg_id} için canlı link çekilemedi.")
        else:
            print(f" -> HATA: '{tvg_id}' ismi boncuk dosyasında bulunamadı.")

    if updated:
        with open(M3U_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n==========================================")
        print(" 'boncuk' DOSYASI GÜNCELLENDİ VE KAYDEDİLDİ")
        print("==========================================")
    else:
        print("\n------------------------------------------")
        print(" HİÇBİR DEĞİŞİKLİK YAPILMADI")
        print("------------------------------------------")

if __name__ == "__main__":
    main()
