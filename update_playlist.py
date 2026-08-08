import json
import re
import urllib.request

M3U_FILE = "boncuk"

def get_youtube_m3u8(youtube_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(youtube_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # HTML içerisinden live hlsManifestUrl (m3u8) adresini yakala
            match = re.search(r'"hlsManifestUrl":"(https:[^"]+)"', html)
            if match:
                raw_url = match.group(1)
                clean_url = raw_url.replace('\\/', '/')
                return clean_url
            
            # Alternatif: Video ID yakalayıp m3u8 adresini türetme
            vid_match = re.search(r'"videoId":"([^"]+)"', html)
            if vid_match:
                video_id = vid_match.group(1)
                return f"https://www.youtube.com/watch?v={video_id}"
                
    except Exception as e:
        print(f"Hata ({youtube_url}): {e}")
    return None

def main():
    try:
        with open('youtube.json', 'r', encoding='utf-8') as f:
            yt_channels = json.load(f)
    except Exception as e:
        print(f"youtube.json okunamadı: {e}")
        return

    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"{M3U_FILE} okunamadı: {e}")
        return

    updated = False

    for channel in yt_channels:
        tvg_id = channel.get('tvg_id', '').strip()
        yt_url = channel.get('youtube_url', '').strip()

        print(f"İşleniyor: {tvg_id}")

        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        if pattern.search(content):
            live_m3u8 = get_youtube_m3u8(yt_url)
            if live_m3u8:
                content = pattern.sub(r'\1' + live_m3u8, content)
                print(f"BAŞARILI: {tvg_id} güncellendi.")
                updated = True
            else:
                print(f"HATA: {tvg_id} için link bulunamadı.")

    if updated:
        with open(M3U_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print("boncuk dosyası başarıyla güncellendi.")

if __name__ == "__main__":
    main()
