import datetime

sabit_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

kanallar = [
    {"adi": "Vavoo Test Kanali", "id": "22284968562a623d1b95b4"}
]

# M3U dosyasının içeriğini hazırlıyoruz
m3u_icerik = "#EXTM3U\n"
# GİT'İN HATA VERMESİNİ ÖNLEMEK İÇİN HER SEFERİNDE DEĞİŞEN ZAMAN DAMGASI
m3u_icerik += f"# Guncelleme Tarihi: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
m3u_icerik += "#EXT-X-USER-AGENT:VAVOO/2.6\n"
m3u_icerik += "#EXT-X-REFERER:https://vavoo.to\n"

for kanal in kanallar:
    m3u_icerik += f"#EXTINF:-1, {kanal['adi']}\n"
    m3u_icerik += f"https://vavoo.tolive/{kanal['id']}.m3u8?key={sabit_token}\n"

# Dosyayı doğrudan ana dizine yazıyoruz
with open("./vavoo_listem.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_icerik)

print("M3U Listesi zaman damgasiyla basariyla olusturuldu!")

