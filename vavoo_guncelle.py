import urllib.request
import re
import os

# IP engeli olmayan, topluluklar tarafından güncellenen kararlı IPTV kaynak havuzları
SOURCES = [
    "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u",
    "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/tr.m3u"
]
TARGET_FILE = "belgesel"

def main():
    if not os.path.exists(TARGET_FILE):
        print(f"Hata: '{TARGET_FILE}' dosyası bulunamadı!")
        return

    print("Mevcut listenizdeki kanallar hafızaya alınıyor...")
    mevcut_kanallar = []
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#EXTINF"):
                parts = line.split(",")
                if len(parts) > 1:
                    kanal_adi = parts[-1].strip()
                    if kanal_adi:
                        mevcut_kanallar.append((line.strip(), kanal_adi.lower()))

    if not mevcut_kanallar:
        print("Listenizde güncellenecek kanal bulunamadı.")
        return

    # Havuzlardaki tüm çalışan linkleri toplayalım
    global_havuz = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for url in SOURCES:
        print(f"Kaynak taranıyor: {url}")
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')
                lines = content.splitlines()
                
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    if line.startswith("#EXTINF"):
                        if i + 1 < len(lines):
                            next_line = lines[i+1].strip()
                            parts = line.split(",")
                            if len(parts) > 1 and next_line.startswith("http"):
                                v_kanal_adi = parts[-1].strip().lower()
                                global_havuz[v_kanal_adi] = next_line
                            i += 2
                            continue
                    i += 1
        except Exception as e:
            print(f"Bu kaynağa bağlanılamadı, geçiliyor: {e}")

    # Yeni M3U içeriğini oluştur (Her cihazda doğrudan açılması için standart başlıklar)
    yeni_m3u_icerik = ["#EXTM3U\n"]
    guncellenen_sayisi = 0

    for orjinal_satir, k_adi_low in mevcut_kanallar:
        eslesme_bulundu = False
        
        # Akıllı isim eşleştirme
        for h_adi, h_link in global_havuz.items():
            if k_adi_low in h_adi or h_adi in k_adi_low:
                yeni_m3u_icerik.append(orjinal_satir + "\n")
                yeni_m3u_icerik.append(h_link + "\n")
                guncellenen_sayisi += 1
                eslesme_bulundu = True
                break
        
        if not eslesme_bulundu:
            # Bulunamazsa listen bozulmasın diye boş bırakmıyoruz, mevcut satırı koruyoruz
            yeni_m3u_icerik.append(orjinal_satir + "\n")
            yeni_m3u_icerik.append("# Kaynak havuzlarda şu an aktif link bulunamadı\n")

    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        f.writelines(yeni_m3u_icerik)

    print(f"Tamamlandı! {guncellenen_sayisi} adet kanal engelsiz yeni linklerle güncellendi.")

if __name__ == "__main__":
    main()
