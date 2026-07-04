import urllib.request
import re

# Doğrudan Vavoo kanallarını içeren güncel topluluk M3U adresi
SOURCE_URL = "https://raw.githubusercontent.com/GeceKod/vivii/refs/heads/main/vavoo_full.m3u"

def main():
    print("Güncel kaynak M3U listesi indiriliyor...")
    
    # Engellenmemek için tarayıcı gibi davranıyoruz
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': '*/*'
    }
    req = urllib.request.Request(SOURCE_URL, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Kaynağa bağlanırken hata oluştu: {e}")
        return

    lines = content.splitlines()
    output_lines = ["#EXTM3U\n"]
    
    # Sadece Türkiye (Turkey) kanallarını yakalamak için (İsterseniz belgesel vb. ekleyebilirsiniz)
    filtreler = ["turkey", "türkiye", "group-title=\"tr\"", "group-title=\"turkey\""]
    
    eklenen_kanal_sayisi = 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                
                # Kanal bilgisinde Türkiye veya TR ifadesi geçiyor mu?
                if any(f in line.lower() for f in filtreler):
                    
                    # Linkin içindeki 20-45 karakter arası karmaşık ID kodunu buluyoruz
                    # Bu regex hem /play/ID/index.m3u8 hem de /play/ID formatlarını yakalar
                    match = re.search(r'play/([a-zA-Z0-9]+)', next_line)
                    
                    # Eğer yukarıdaki yakalayamazsa, linkteki son eğik çizgiden sonrasını veya nokta öncesini dene
                    if not match:
                        match = re.search(r'/([a-zA-Z0-9]{20,45})(?:\.|/|$)', next_line)
                    
                    if match:
                        kanal_id = match.group(1)
                        
                        # TAM OLARAK İSTEDİĞİNİZ BİÇİM:
                        yeni_link = f"https://vavoo.to/vavoo-iptv/play/{kanal_id}"
                        
                        output_lines.append(line + "\n")
                        output_lines.append(yeni_link + "\n")
                        eklenen_kanal_sayisi += 1
                        
                i += 2
                continue
        i += 1

    # Çıktıyı deponuzdaki 'belgesel' dosyasına yazıyoruz
    with open("belgesel", "w", encoding="utf-8") as f:
        f.writelines(output_lines)
        
    print(f"İşlem tamamlandı! '{eklenen_kanal_sayisi}' adet Türkiye kanalı dönüştürülerek yazıldı.")

if __name__ == "__main__":
    main()
