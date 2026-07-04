import urllib.request
import re

# Güncel Vavoo M3U kaynak adresi
SOURCE_URL = "https://raw.githubusercontent.com/GeceKod/vivii/refs/heads/main/vavoo_Turkey.m3u"

def main():
    print("M3U kaynak listesi indiriliyor...")
    
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
    
    # Sadece belgesel odaklı kanalları yakalamak için filtre listesi
    belgesel_filtreleri = [
        "belgesel", "documentary", "nat geo", "national geographic", 
        "discovery", "history", "science", "animal planet", 
        "viasat", "tlc", "dmax", "investigation discovery", "id hd"
    ]
    
    eklenen_kanal_sayisi = 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                
                # Kanal adında veya grup başlığında belgesel kelimeleri geçiyor mu?
                channel_text = line.lower()
                if any(f in channel_text for f in belgesel_filtreleri):
                    
                    # Link içindeki benzersiz ID kodunu izole ediyoruz
                    match = re.search(r'play/([a-zA-Z0-9]+)', next_line)
                    
                    if not match:
                        match = re.search(r'/([a-zA-Z0-9]{20,45})(?:\.|/|$)', next_line)
                    
                    if match:
                        kanal_id = match.group(1)
                        
                        # İSTEDİĞİNİZ BİÇİM:
                        yeni_link = f"https://vavoo.to/vavoo-iptv/play/{kanal_id}"
                        
                        output_lines.append(line + "\n")
                        output_lines.append(yeni_link + "\n")
                        eklenen_kanal_sayisi += 1
                        
                i += 2
                continue
        i += 1

    # Çıktıyı doğrudan 'belgesel' isimli dosyanıza yazar
    with open("belgesel", "w", encoding="utf-8") as f:
        f.writelines(output_lines)
        
    print(f"İşlem tamamlandı! Toplam '{eklenen_kanal_sayisi}' adet belgesel kanalı formatlanarak yazıldı.")

if __name__ == "__main__":
    main()
