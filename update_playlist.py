import json
import re
import yt_dlp

M3U_FILE = "boncuk"

def get_live_m3u8(youtube_url):
    ydl_opts = {'format': 'best', 'quiet': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            return info.get('url')
    except Exception as e:
        print(f"Hata ({youtube_url}): {e}")
        return None

def main():
    # 1. youtube.json dosyasını oku
    try:
        with open('youtube.json', 'r', encoding='utf-8') as f:
            yt_channels = json.load(f)
    except FileNotFoundError:
        print("HATA: youtube.json bulunamadı!")
        return

    # 2. boncuk dosyasını oku
    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"HATA: '{M3U_FILE}' dosyası bulunamadı!")
        return

    # 3. Her kanal için metin içinden yerini bul ve linkini güncelle
    for channel in yt_channels:
        tvg_id = channel.get('tvg_id', '').strip()
        yt_url = channel.get('youtube_url', '').strip()

        if not tvg_id or not yt_url:
            continue

        print(f"Aranıyor: {tvg_id}")

        # Regex açıklaması:
        # #EXTINF metninden başlayarak tvg-id="KANAL_ADI" içeren kısmı ve 
        # devamındaki ilk http/https linkini yakalar.
        pattern = re.compile(
            r'(#EXTINF:[^\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\n]*?\n)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        match = pattern.search(content)
        if match:
            print(f"Eşleşti! Canlı link çekiliyor: {tvg_id}")
            live_url = get_live_m3u8(yt_url)

            if live_url:
                # Sadece ilgili kanalın hemen altındaki linki yenisiyle değiştirir
                content = pattern.sub(r'\1' + live_url, content)
                print(f"BAŞARILI: {tvg_id} güncellendi.")
            else:
                print(f"UYARI: {tvg_id} için canlı link alınamadı.")
        else:
            print(f"BULUNAMADI: '{tvg_id}' id'si {M3U_FILE} içinde eşleşmedi. Büyük/küçük harfleri kontrol edin.")

    # 4. Güncellenmiş içeriği kaydet
    with open(M3U_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    print("İşlem tamamlandı.")

if __name__ == "__main__":
    main()
