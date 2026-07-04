import datetime

# Sabit uzun ömürlü güvenli anahtarımız
sabit_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# Sizin listenizdeki tüm gerçek belgesel kanalları ve bilgileri
kanallar = [
    {
        "adi": "Tarih TV", 
        "id": "3856957052050da882aa10",
        "logo": "https://www.dsmart.com.tr/api/v1/public/images/kanallar/tarihtv.png",
        "tvg_id": "TARİH TV.tr"
    },
    {
        "adi": "BBC earth", 
        "id": "22284968562a623d1b95b4",
        "logo": "https://www.creativeboom.com/upload/articles/8f/8f6cd51ec38e4f9ccab6a7350ba42d4ca9c429da_1280.png",
        "tvg_id": "BBC EARTH.tr"
    },
    {
        "adi": "History", 
        "id": "1335130209de4b92f31496",
        "logo": "https://www.dsmart.com.tr/api/v1/public/images/kanallar/History%20Logo%20on%20Black%20BG.PNG",
        "tvg_id": "VIASAT HISTORY.tr"
    },
    {
        "adi": "Discovery", 
        "id": "6957057788f10364acdac",
        "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/aaac1290-6d58-4036-b106-a7026a4c1bfc.png",
        "tvg_id": "DISCOVERY CHANNEL.tr"
    },
    {
        "adi": "Discovery ID", 
        "id": "20954040600611bde9e160",
        "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/539be808-86e7-4ed2-aa0b-130dbc1ac450.png",
        "tvg_id": "ID.tr"
    },
    {
        "adi": "Nat Geo Wild", 
        "id": "1324166169d75d5197aa7",
        "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/0/0/Vod/HLS/4cc38817-6eb0-4f26-ac2b-cb5baa3b68ba.png",
        "tvg_id": "NATIONAL GEOGRAPHIC WILD.tr"
    },
    {
        "adi": "Nat Geo", 
        "id": "1960546091bcaf052d3800",
        "logo": "https://feo.kablowebtv.com/resize/168A635D265A4328C2883FB4CD8FF/500/500/channels/logos/38a2e51a-9f7f-4915-aa88-f78190f59411.png",
        "tvg_id": "NATIONAL GEOGRAPHIC.tr"
    },
    {
        "adi": "Love nature", 
        "id": "259380083927b83aced3e1",
        "logo": "https://lovenature.com/wp-content/uploads/2020/08/love-nature-logo_peacock.png",
        "tvg_id": "Love nature"
    },
    {
        "adi": "Agro Tv", 
        "id": "163358782054d9002fa0b0",
        "logo": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTwwcj38tD2WBf6XQWRDtP56BqKxp0huHjYDDzXwy0bzvhGxit9ImXwVjE&s=10",
        "tvg_id": "Agro Tv"
    }
]

m3u_icerik = "#EXTM3U\n"
m3u_icerik += f"# Guncelleme: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
m3u_icerik += "#EXT-X-USER-AGENT:VAVOO/2.6\n"
m3u_icerik += "#EXT-X-REFERER:https://vavoo.to/\n"

# Vavoo kanallarını otomatik taze şifreli olarak ekliyoruz
for kanal in kanallar:
    m3u_icerik += f'#EXTINF:-1 group-title="BELGESEL" tvg-id="{kanal["tvg_id"]}" tvg-logo="{kanal["logo"]}" ,{kanal["adi"]}\n'
    m3u_icerik += f"https://vavoo.to{kanal['id']}.m3u8?key={sabit_token}\n"

# Vavoo olmayan sabit normal m3u8 linklerinizi de listenin sonuna ekliyoruz (Bunlar şifresizdir)
m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="TRT GENÇ.tr" tvg-logo="https://pbs.twimg.com/profile_images/2009963534021459968/JwBVdge0_400x400.jpg" ,TRT GENÇ\n'
m3u_icerik += 'https://tv-trtgenc.medya.trt.com.tr/master.m3u8\n'

m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="YabanTV.tr" tvg-logo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRR2EalQKrrB5JxrjDcEMHl-IXVYvYyv3Kqng&s" ,Yaban TV\n'
m3u_icerik += 'https://trn03.tulix.tv/gt-yabantv/tracks-v1a1/mono.m3u8?token=0631e8753bcdf25bb2a5015db22ec082\n'

m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="TRT BELGESEL.tr" tvg-logo="https://cdn.technettv.com/channel/20609/logo_256_1699961655.png" ,TRT Belgesel\n'
m3u_icerik += 'https://tv-trtbelgesel.medya.trt.com.tr/master.m3u8\n'

# Dosyayı yazdırıyoruz
with open("./vavoo_listem.m3u", "w", encoding="utf-8") as f:
    f.write(m3u_icerik)

print("Tüm belgesel listesi başarıyla güncellendi!")
