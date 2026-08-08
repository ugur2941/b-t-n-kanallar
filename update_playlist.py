import json
import re
import subprocess

M3U_FILE = "boncuk"

def get_live_m3u8(youtube_url):
    """
    1. Yöntem: yt-dlp ile iOS/Android client simülasyonu
    """
    cmd_ytdlp = [
        "yt-dlp",
        "-g",
        "-f", "best",
        "--no-warnings",
        "--no-cache-dir",
        "--extractor-args", "youtube:player_client=ios,android,web_creator",
        youtube_url
    ]
    
    try:
        res = subprocess.run(cmd_ytdlp, capture_output=True, text=True, timeout=30)
        if res.returncode == 0:
            lines = [line.strip() for line in res.stdout.strip().split('\n') if line.strip()]
            for line in lines:
                if ".m3u8" in line or "manifest" in line or "googlevideo.com" in line:
                    return line
            if lines:
                return lines[0]
        else:
            print(f"      [yt-dlp Denemesi Başarısız]: {res.stderr.strip()[:120]}")
    except Exception as e:
        print(f"      [yt-dlp Exception]: {e}")

    """
    2. Yöntem (Yedek): streamlink ile bot korumasını aşma
    """
    print("   -> Fallback: 'streamlink' ile deneniyor...")
    cmd_streamlink = [
        "streamlink",
        "--stream-url",
        youtube_url,
        "best"
    ]
    try:
        res_sl = subprocess.run(cmd_streamlink, capture_output=True, text=True, timeout=30)
        if res_sl.returncode == 0:
            url = res_sl.stdout.strip()
            if url.startswith("http"):
                return url
        else:
            print(f"      [streamlink Hata]: {res_sl.stderr.strip()[:120]}")
    except Exception as e:
        print(f"      [streamlink Exception]: {e}")

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

    updated_count = 0

    print("--- 3. Güncelleme İşlemi Başlıyor ---")
    for channel in yt_channels:
        tvg_id = channel.get('tvg_id', '').strip()
        yt_url = channel.get('youtube_url', '').strip()

        print(f"\n[Kanal]: '{tvg_id}'")
        print(f" -> Hedef URL: {yt_url}")

        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        match = pattern.search(content)
        if match:
            old_url = match.group(2)
            print(f" -> Bulunan Eski Link: {old_url[:65]}...")
            
            live_url = get_live_m3u8(yt_url)

            if live_url:
                if old_url == live_url:
                    print(f" -> UYARI: Çekilen yeni link eski link ile BİREBİR AYNI.")
                else:
                    content = pattern.sub(r'\1' + live_url, content)
                    print(f" -> BAŞARILI: Yeni link güncellendi!")
                    print(f"    Yeni Link: {live_url[:65]}...")
                    updated_count += 1
            else:
                print(f" -> HATA: İki yöntemle de canlı m3u8 linki çıkarılamadı.")
        else:
            print(f" -> HATA: '{tvg_id}' tvg-id değeri 'boncuk' dosyasında bulunamadı!")

    if updated_count > 0:
        with open(M3U_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n==========================================")
        print(f" Toplam {updated_count} kanal güncellendi ve 'boncuk' dosyasına yazıldı.")
        print(f"==========================================")
    else:
        print("\n------------------------------------------")
        print(" HİÇBİR DEĞİŞİKLİK YAPILMADI VEYA DOSYAYA PUSH EDİLMEDİ")
        print("------------------------------------------")

if __name__ == "__main__":
    main()
