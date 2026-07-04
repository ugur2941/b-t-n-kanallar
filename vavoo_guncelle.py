import urllib.request
import json
import ssl

# SSL sertifika hatalarını göz ardı etmek için (Gerekirse)
ssl_context = ssl._create_unverified_context()

def get_vavoo_channels():
    # 1. Vavoo API'sinden güncel kanal listesini JSON formatında çekiyoruz
    api_url = "https://www.vavoo.to/vavoo/channels"
    req = urllib.request.Request(api_url, headers={'User-Agent': 'VAVOO/2.6'})
    
    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            channels = json.loads(response.read().decode('utf-8'))
            return channels
    except Exception as e:
        print(f"Vavoo API'sine bağlanılamadı: {e}")
        return []

def main():
    channels = get_vavoo_channels()
    if not channels:
        print("Kanal listesi boş döndü veya alınamadı.")
        return

    output_lines = ["#EXTM3U\n"]
    
    # Filtrelemek istediğiniz kategoriler veya anahtar kelimeler
    # Türkiye kanalları için genellikle grup adı veya ülke kodu kontrol edilir
    filtreler = ["belgesel", "documentary", "nat geo", "discovery", "history"]

    for channel in channels:
        # Vavoo API çıktısında genellikle 'id', 'name', 'group', 'country' gibi alanlar bulunur
        channel_id = channel.get("id")
        name = channel.get("name", "Bilinmeyen Kanal")
        group = channel.get("group", "Genel")
        country = channel.get("country", "").lower()

        # Sadece Türkiye kanalları veya belirli belgesel kelimelerini içeren kanalları süzüyoruz
        is_turkish = (country == "turkey" or country == "tr")
        is_documentary = any(f in name.lower() or f in group.lower() for f in filtreler)

        if is_turkish or is_documentary:
            # İstediğiniz link formatını oluşturuyoruz:
            # Örnek: https://vavoo.to/vavoo-iptv/play/KanalID
            stream_url = f"https://vavoo.to/vavoo-iptv/play/{channel_id}"
            
            # M3U Formatına dönüştürme
            output_lines.append(f'#EXTINF:-1 tvg-id="{channel_id}" group-title="{group.capitalize()}",{name}\n')
            output_lines.append(f"{stream_url}\n")

    # Sonuçları 'belgesel' dosyasına kaydet
    with open("belgesel", "w", encoding="utf-8") as f:
        f.writelines(output_lines)
        
    print(f"Güncelleme tamamlandı! 'belgesel' dosyasına {len(output_lines) // 2} kanal yazıldı.")

if __name__ == "__main__":
    main()

