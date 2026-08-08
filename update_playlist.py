import json
import re
import yt_dlp

# Deponuzdaki M3U dosyasının tam adı
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
    # 1. youtube.json dosyasından güncellenecek YouTube kanallarını oku
    try:
        with open('youtube.json', 'r', encoding='utf-8') as f:
            yt_channels = json.load(f)
    except FileNotFoundError:
        print("HATA: youtube.json dosyası bulunamadı!")
        return

    yt_map = {item['tvg_id']: item['youtube_url'] for item in yt_channels}

    # 2. 'boncuk' dosyasındaki mevcut kanalları oku
    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"HATA: '{M3U_FILE}' dosyası depoda bulunamadı!")
        return

    updated_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        updated_lines.append(line)

        # #EXTINF satırındaki tvg-id değerini yakala
        if line.startswith("#EXTINF"):
            match = re.search(r'tvg-id="([^"]+)"', line)
            if match:
                tvg_id = match.group(1)
                
                # Eğer bu tvg-id 'youtube.json' içinde varsa linkini güncelle
                if tvg_id in yt_map:
                    yt_url = yt_map[tvg_id]
                    print(f"Güncelleniyor: {tvg_id}")
                    live_url = get_live_m3u8(yt_url)
                    
                    if live_url and (i + 1) < len(lines):
                        updated_lines.append(f"{live_url}\n")
                        i += 2  # Eski/geçersiz URL satırını atla
                        continue

        i += 1

    # 3. Diğer tüm kanallara dokunmadan güncellenmiş halini 'boncuk' dosyasına yaz
    with open(M3U_FILE, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print("'boncuk' dosyası başarıyla güncellendi.")

if __name__ == "__main__":
    main()
