import datetime

# ... (Kanal listesi ve sabit linkler)
# Sabit uzun ömürlü güvenli anahtarımız
sabit_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# ... (Kanal verileri)

m3u_icerik = "#EXTM3U\n"
# ... (Başlık ve referer bilgisi)

# ... (Döngü ile link oluşturma)

with open("./belgesel", "w", encoding="utf-8") as f:
    f.write(m3u_icerik)

print("Listeniz doğrudan belgesel dosyasına başarıyla güncellendi!")
