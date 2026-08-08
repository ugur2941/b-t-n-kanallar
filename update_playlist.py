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
        print(f"yt-dlp Hatası ({youtube_url}): {e}")
        return None

def main():
    print("--- 1. youtube.json Okunuyor ---")
    try:
        with open('youtube.json', 'r', encoding='utf-8') as f:
            yt_channels = json.load(f)
            print(f"Yüklenen kanallar: {yt_channels}")
    except Exception as e:
        print(f"HATA: youtube.json okunamadı -> {e}")
        return

    print("\n--- 2. boncuk Dosyası Okunuyor ---")
    try:
        with open(M3U_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"boncuk dosyası başarıyla okundu. Toplam karakter sayısı: {len(content)}")
            # Dosya başından bir kesit göster
            print("Dosya İçeriği İlk 300 Karakter:")
            print(repr(content[:300]))
    except Exception as e:
        print(f"HATA: '{M3U_FILE}' okunamadı -> {e}")
        return

    updated = False

    print("\n--- 3. Eşleşme ve Güncelleme Başlıyor ---")
    for channel in yt_channels:
        tvg_id = channel.get('tvg_id', '').strip()
        yt_url = channel.get('youtube_url', '').strip()

        print(f"\n[Aranıyor]: '{tvg_id}'")

        # Esnek Regex: #EXTINF ile başlayan ve ilgili tvg-id'yi içeren bloğu arar
        # Satır sonu karakteri farklarını (\r\n veya \n) tolere eder
        pattern = re.compile(
            r'(#EXTINF:[^\r\n]*?tvg-id="' + re.escape(tvg_id) + r'"[^\r\n]*?[\r\n]+)(https?://[^\s\r\n]+)',
            re.IGNORECASE
        )

        match = pattern.search(content)
        if match:
            print(f"-> Eşleşme Bulundu!")
            print(f"   Bulunan Header: {repr(match.group(1))}")
            print(f"   Eski Link: {repr(match.group(2))}")

            live_url = get_live_m3u8(yt_url)
            if live_url:
                content = pattern.sub(r'\1' + live_url, content)
                print(f"   Yeni Link Yerleştirildi: {live_url[:60]}...")
                updated = True
            else:
                print("   HATA: YouTube canlı yayın adresi alınamadı!")
        else:
            print(f"-> BULUNAMADI: '{tvg_id}' deseni metinde eşleşmedi.")

    if updated:
        with open(M3U_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n--- İŞLEM BAŞARIYLA TAMAMLANDI VE 'boncuk' KAYDEDİLDİ ---")
    else:
        print("\n--- HİÇBİR DEĞİŞİKLİK YAPILMADI ---")

if __name__ == "__main__":
    main()
