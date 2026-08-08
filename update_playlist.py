import json
import re
import subprocess

M3U_FILE = "boncuk"

def get_live_m3u8_ytdlp(youtube_url):
    """
    yt-dlp kullanarak YouTube canlı yayınından ham .m3u8 linkini çeker.
    """
    try:
        # yt-dlp -g -f best [URL] komutu doğrudan .m3u8 linkini döner
        cmd = [
            "yt-dlp",
            "-g",
            "-f", "best",
            "--no-warnings",
            youtube_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        
        if result.returncode == 0:
            url = result.stdout.strip()
            if ".m3u8" in url or "manifest" in url:
                return url
        else:
            print(f"   [yt-dlp Hata]: {result.stderr.strip()}")
    except Exception as e:
        print(f"   [yt-dlp Çalıştırılamadı]: {e}")

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
            print(f" -> Eşleşti, yt-dlp ile ham canlı .m3u8 adresi çekiliyor...")
            live_url = get_live_m3u8_ytdlp(yt_url)

            if live_url:
                content = pattern.sub(r'\1' + live_url, content)
                print(f" -> BAŞARILI: {tvg_id} ham .m3u8 linki alındı!")
                print(f"    Gerçek Link: {live_url[:80]}...")
                updated = True
            else:
                print(f" -> HATA: {tvg_id} için yt-dlp canlı link çıkaramadı.")
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
