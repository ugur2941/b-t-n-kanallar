import urllib.request
import re

# Kanalların çekileceği ana kaynak M3U adresi
SOURCE_URL = "https://raw.githubusercontent.com/fokus-ocas/ip/main/vavoo.m3u"

def main():
    print("Güncel kaynak M3U listesi indiriliyor...")
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Kaynağa bağlanırken hata oluştu: {e}")
        return

    lines = content.splitlines()
    output_lines = ["#EXTM3U\n"]
    
    # Türkiye (Turkey) veya Belgesel içeren kanalları filtrelemek için kelimeler
    filtreler = ["turkey", "türkiye", "belgesel", "documentary", "nat geo", "discovery", "history"]
    
    eklenen_kanal_sayisi = 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                
                # Kanal isminde veya grup başlığında filtre kelimelerimiz var mı?
                if any(f in line.lower() for f in filtreler):
                    
                    # Regex ile link içindeki 20-40 karakter arası benzersiz ID'yi yakalıyoruz
                    # Örn: .../play/3856957052050da882aa10/index.m3u8 içindeki ID'yi ayıklar
                    match = re.search(r'(?:play/|/)([a-zA-Z0-9]{15,45})', next_line)
                    
                    if match:
                        kanal_id = match.group(1)
                        
                        # İSTEDİĞİNİZ ÖZEL FORMAT:
                        yeni_link = f"https://vavoo.to/vavoo-iptv/play/{kanal_id}"
                        
                        output_lines.append(line + "\n")
                        output_lines.append(yeni_link + "\n")
                        eklenen_kanal_sayisi += 1
                        
                i += 2
                continue
        i += 1

    # Çıktıyı doğrudan 'belgesel' dosyasına kaydediyoruz
    with open("belgesel", "w", encoding="utf-8") as f:
        f.writelines(output_lines)
        
    print(f"İşlem başarıyla tamamlandı! '{eklenen_kanal_sayisi}' adet kanal istediğiniz formatta 'belgesel' dosyasına yazıldı.")

if __name__ == "__main__":
    main()
