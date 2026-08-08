import json
import re
import urllib.request

M3U_FILE = "boncuk"

def get_live_m3u8(youtube_url):
    """
    Önce doğrudan YouTube HTML'inden, başarısız olursa Cloudflare/Proxy 
    servislerinden canlı .m3u8 adresini yakalamaya çalışır.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    # 1. YÖNTEM: Doğrudan YouTube HTML'i
    try:
        req = urllib.request.Request(youtube_url, headers=headers)
        with urllib.request.urlopen(req, timeout=12) as response:
            html = response.read().decode('utf-8')
            match = re.search(r'"hlsManifestUrl":"(https:[^"]+)"', html)
            if match:
                return match.group(1).replace('\\/', '/').replace('\\u0026', '&')
    except Exception as e:
        print(f"   [1. Yöntem Başarısız]: Direct YouTube -> {e}")

    # 2. YÖNTEM: Alternatif Proxy / Scrape Uç Noktaları
    match_handle = re.search(r'@([^/]+)', youtube_url)
    if match_handle:
        handle = match_handle.group(1)
        proxies = [
            f"https://yt.artemislena.eu/live/{handle}",
            f"https://inv.tux.pizza/live/{handle}"
        ]
        for p_url in proxies:
            try:
                req = urllib.request.Request(p_url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode('utf-8')
                    m3u8_match = re.search(r'https?://[^\s"<>\']+\.m3u8[^\s"<>\']*', html)
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

        print(f"\n[Kanal Aranıyor]: '{tvg_id}'")

        # Esnek Regex: tvg-id="Sözcü Tv.tr" içeren satırı ve hemen altındaki URL'yi bulur
        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        if pattern.search(content):
            print(f" -> '{tvg_id}' boncuk dosyasında bulundu! m3u8 çekiliyor...")
            live_url = get_live_m3u8(yt_url)

            if live_url:
                content = pattern.sub(r'\1' + live_url, content)
                print(f" -> BAŞARILI: Yeni .m3u8 adresi yazıldı!")
                print(f"    Yeni Link: {live_url[:60]}...")
                updated = True
            else:
                print(f" -> HATA: Live m3u8 linki çekilemedi (YouTube/API engeli).")
        else:
            print(f" -> HATA/BULUNAMADI: '{tvg_id}' ismi 'boncuk' dosyasında birebir eşleşmedi!")

    if updated:
        with open(M3U_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n==========================================")
        print(" 'boncuk' DOSYASI GÜNCELLENDİ VE KAYDEDİLDİ")
        print("==========================================")
    else:
        print("\n------------------------------------------")
        print(" HİÇBİR DEĞİŞİKLİK YAPILMADI (Eşleşme/Link Yok)")
        print("------------------------------------------")

if __name__ == "__main__":
    main()
