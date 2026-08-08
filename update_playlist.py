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
    # 1. youtube.json oku
    try:
        with open('youtube.json', 'r', encoding='utf-8') as f:
            yt_channels = json.load(f)
    except FileNotFoundError:
        print("HATA: youtube.json bulunamadı!")
        return

    # tvg_id küçük harfe çevrilerek harf duyarlılığı kaldırılır
    yt_map = {item['tvg_id'].strip().lower(): item['youtube_url'] for item in yt_channels}

    # 2. boncuk dosyasını oku
    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"HATA: '{M3U_FILE}' dosyası bulunamadı!")
        return

    updated_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        updated_lines.append(line)

        if line.startswith("#EXTINF"):
            match = re.search(r'tvg-id="([^"]+)"', line, re.IGNORECASE)
            if match:
                tvg_id_file = match.group(1).strip().lower()
                
                # Eşleşme kontrolü
                if tvg_id_file in yt_map:
                    yt_url = yt_map[tvg_id_file]
                    print(f"Eşleşti, link çekiliyor: {match.group(1)}")
                    live_url = get_live_m3u8(yt_url)
                    
                    if live_url:
                        # Bir sonraki satır eski link ise atla ve yenisini koy
                        if (i + 1) < len(lines) and lines[i + 1].strip().startswith("http"):
                            updated_lines.append(f"{live_url}\n")
                            i += 1  # Eski URL satırını atla
                        else:
                            updated_lines.append(f"{live_url}\n")
                        i += 1
                        continue

        i += 1

    # 3. Güncellenmiş halini dosyaya yaz
    with open(M3U_FILE, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

    print("İşlem tamamlandı.")

if __name__ == "__main__":
    main()
