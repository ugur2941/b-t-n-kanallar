import datetime

# Sabit uzun ömürlü güvenli anahtarımız
sabit_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# Sizin orijinal listenizdeki tüm belgesel kanalları ve logoları
kanallar = [
    {
        "adi": "Tarih TV", 
        "id": "3856957052050da882aa10",
        "logo": "https://dsmart.com.tr",
        "tvg_id": "TARİH TV.tr"
    },
    {
        "adi": "BBC earth", 
        "id": "22284968562a623d1b95b4",
        "logo": "https://creativeboom.com",
        "tvg_id": "BBC EARTH.tr"
    },
    {
        "adi": "History", 
        "id": "1335130209de4b92f31496",
        "logo": "https://dsmart.com.tr",
        "tvg_id": "VIASAT HISTORY.tr"
    },
    {
        "adi": "Discovery", 
        "id": "6957057788f10364acdac",
        "logo": "https://kablowebtv.com",
        "tvg_id": "DISCOVERY CHANNEL.tr"
    },
    {
        "adi": "Discovery ID", 
        "id": "20954040600611bde9e160",
        "logo": "https://kablowebtv.com",
        "tvg_id": "ID.tr"
    },
    {
        "adi": "Nat Geo Wild", 
        "id": "1324166169d75d5197aa7",
        "logo": "https://kablowebtv.com",
        "tvg_id": "NATIONAL GEOGRAPHIC WILD.tr"
    },
    {
        "adi": "Nat Geo", 
        "id": "1960546091bcaf052d3800",
        "logo": "https://kablowebtv.com",
        "tvg_id": "NATIONAL GEOGRAPHIC.tr"
    },
    {
        "adi": "Love nature", 
        "id": "259380083927b83aced3e1",
        "logo": "https://lovenature.com",
        "tvg_id": "Love nature"
    },
    {
        "adi": "Agro Tv", 
        "id": "163358782054d9002fa0b0",
        "logo": "https://gstatic.com",
        "tvg_id": "Agro Tv"
    }
]

# M3U Dosyasını hazırlamaya başlıyoruz
m3u_icerik = "#EXTM3U\n"
m3u_icerik += f"# Guncelleme: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
m3u_icerik += "#EXT-X-USER-AGENT:VAVOO/2.6\n"
m3u_icerik += "#EXT-X-REFERER:https://vavoo.to\n"

# Vavoo kanallarını listeye döngüyle ekliyoruz
for kanal in kanallar:
    m3u_icerik += f'#EXTINF:-1 group-title="BELGESEL" tvg-id="{kanal["tvg_id"]}" tvg-logo="{kanal["logo"]}" ,{kanal["adi"]}\n'
    m3u_icerik += f"https://vavoo.tolive/{kanal['id']}.m3u8?key={sabit_token}\n"

# Vavoo altyapısında olmayan diğer normal sabit belgesel kanallarınız
m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="TRT GENÇ.tr" tvg-logo="https://twimg.com" ,TRT GENÇ\n'
m3u_icerik += 'https://trt.com.tr\n'

m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="YabanTV.tr" tvg-logo="https://gstatic.com" ,Yaban TV\n'
m3u_icerik += 'https://tulix.tv\n'

m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="TRT BELGESEL.tr" tvg-logo="https://technettv.com" ,TRT Belgesel\n'
m3u_trt_link = 'https://trt.com.tr'
m3u_icerik += f"{m3u_trt_link}\n"

# Hazırlanan tüm listeyi doğrudan uygulamanızın bağlı olduğu "belgesel" dosyasına yazıyoruz
with open("./belgesel", "w", encoding="utf-8") as f:
    f.write(m3u_icerik)

print("Listeniz doğrudan belgesel dosyasına başarıyla güncellendi!")
