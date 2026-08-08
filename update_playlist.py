import json
import re
import yt_dlp

M3U_FILE = "boncuk"

def get_live_m3u8(youtube_url):
    # TV ve Android Embed istemcilerini kullanarak IP engelini aşma
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['tv_embedded', 'android', 'web_creator'],
                'player_skip': ['webpage', 'configs']
            }
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            
            # Yayın adresini kontrol et
            if 'url' in info:
                return info['url']
            elif 'manifest_url' in info:
                return info['manifest_url']
            elif 'entries' in info and len(info['entries']) > 0:
                return info['entries'][0].get('url')
            return None
    except Exception as e:
        print(f"yt-dlp Hatası ({youtube_url}): {e}")
        return None

def main():
    print("--- 1. youtube.json Okunuyor ---")
    try:
        with open('youtube.json', 'r', encoding='utf-8') as f:
            yt_channels = json.load(f)
    except Exception as e:
        print(f"HATA: youtube.json okunamadı -> {e}")
        return

    print("\n--- 2. boncuk Dosyası Okunuyor ---")
    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"HATA: '{M3U_FILE}' okunamadı -> {e}")
        return

    updated = False

    print("\n--- 3. Eşleşme ve Güncelleme Başlıyor ---")
    for channel in yt_channels:
        tvg_id = channel.get('tvg_id', '').strip()
        yt_url = channel.get('youtube_url', '').strip()

        print(f"\n[İşleniyor]: '{tvg_id}' -> {yt_url}")

        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        match = pattern.search(content)
        if match:
            print(f"-> Eşleşme bulundu, canlı yayın adresi çekiliyor...")
            live_url = get_live_m3u8(yt_url)
            
            if live_url:
                content = pattern.sub(r'\1' + live_url, content)
                print(f"-> BAŞARILI: {tvg_id} linki güncellendi!")
                updated = True
            else:
                print(f"-> HATA: {tvg_id} canlı yayın adresi alınamadı.")
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
