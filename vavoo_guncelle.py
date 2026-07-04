import urllib.request
import re

# Vavoo verilerini anlık çözen ve güncelleyen açık kaynak havuz listesi
SOURCE_URL = "https://raw.githubusercontent.com/fokus-ocas/ip/main/vavoo.m3u"

def main():
    print("Güncel kaynak listesi indiriliyor...")
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Kaynağa bağlanırken hata oluştu: {e}")
        return

    lines = content.splitlines()
    output_lines = ["#EXTM3U\n"]
    
    # Türkiye (Turkey) veya Belgesel içeren kanalları yakalamak için filtreler
    # Eğer sadece Türkiye kanallarını istiyorsanız listeyi ona göre düzenleyebilirsiniz
    filtreler = ["turkey", "türkiye", "belgesel", "documentary", "nat geo", "discovery"]
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            # Bir sonraki satırın yayın linki olduğunu doğrula
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                
                # Kanal bilgisinde filtre kelimelerimiz geçiyor mu kontrol et
                if any(f in line.lower() for f in filtreler):
                    
                    # Orijinal link içinden sadece kanalın ID/Key kısmını regex ile ayıklıyoruz
                    # Örn: .../play/123456abcdef veya .../123456abcdef.ts içindeki benzersiz kodu alır
                    match = re.search(r'(?:play/|/)([a-zA-Z0-9]{15,40})', next_line)
                    
                    if match:
                        kanal_id = match.group(1)
                        # İstediğiniz temiz formatı oluşturuyoruz
                        yeni_link = f"https://vavoo.to/vavoo-iptv/play/{kanal_id}"
                        
                        output_lines.append(line + "\n")
                        output_lines.append(yeni_link + "\n")
                        
                i += 2
                continue
        i += 1

    # Çıktıyı 'belgesel' dosyasına yazıyoruz
    with open("belgesel", "w", encoding="utf-8") as f:
        f.writelines(output_lines)
        
    print(f"İşlem tamam! Toplam {len(output_lines) // 2} adet Türkiye/Belgesel kanalı eklendi.")

if __name__ == "__main__":
    main()
