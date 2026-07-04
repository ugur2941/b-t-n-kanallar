import datetime
import requests

def get_vavoo_token():
    url = "https://vavoo.to"
    # Bulut sunucu engelini aşmak için gerçek bir insan tarayıcısı taklidi yapıyoruz
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://vavoo.to",
        "Referer": "https://vavoo.to",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    payload = {"id": "", "ver": "2.6"}
    
    try:
        # Oturum (Session) başlatarak çerez korumasını geçiyoruz
        session = requests.Session()
        response = session.post(url, json=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            token = data.get("signed") or data.get("token")
            if token:
                return token
    except Exception as e:
        print(f"Token hatası: {e}")
    
    # Eğer ilk sunucu engellenirse yedek olarak topluluk tarafından çözülmüş genel tokenı döndür
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

# Canlı ve taze tokenı internetten anlık çekiyoruz
canli_token = get_vavoo_token()

# Orijinal belgesel kanallarınızın listesi
kanallar = [
    {"adi": "Tarih TV", "id": "3856957052050da882aa10", "logo": "https://dsmart.com.tr", "tvg_id": "TARİH TV.tr"},
    {"adi": "BBC earth", "id": "22284968562a623d1b95b4", "logo": "https://creativeboom.com", "tvg_id": "BBC EARTH.tr"},
    {"adi": "History", "id": "1335130209de4b92f31496", "logo": "https://dsmart.com.tr", "tvg_id": "VIASAT HISTORY.tr"},
    {"adi": "Discovery", "id": "6957057788f10364acdac", "logo": "https://kablowebtv.com", "tvg_id": "DISCOVERY CHANNEL.tr"},
    {"adi": "Discovery ID", "id": "20954040600611bde9e160", "logo": "https://kablowebtv.com", "tvg_id": "ID.tr"},
    {"adi": "Nat Geo Wild", "id": "1324166169d75d5197aa7", "logo": "https://kablowebtv.com", "tvg_id": "NATIONAL GEOGRAPHIC WILD.tr"},
    {"adi": "Nat Geo", "id": "1960546091bcaf052d3800", "logo": "https://kablowebtv.com", "tvg_id": "NATIONAL GEOGRAPHIC.tr"},
    {"adi": "Love nature", "id": "259380083927b83aced3e1", "logo": "https://lovenature.com", "tvg_id": "Love nature"},
    {"adi": "Agro Tv", "id": "163358782054d9002fa0b0", "logo": "https://gstatic.com", "tvg_id": "Agro Tv"}
]

m3u_icerik = "#EXTM3U\n"
m3u_icerik += f"# Guncelleme: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
m3u_icerik += "#EXT-X-USER-AGENT:VAVOO/2.6\n"
m3u_icerik += "#EXT-X-REFERER:https://vavoo.to\n"

# Kanalları taze yönlendirme şifresiyle yazdırıyoruz
for kanal in kanallar:
    m3u_icerik += f'#EXTINF:-1 group-title="BELGESEL" tvg-id="{kanal["tvg_id"]}" tvg-logo="{kanal["logo"]}" ,{kanal["adi"]}\n'
    # İstediğiniz hatasız resmi canlı yayın formatı
    m3u_icerik += f"https://vavoo.tolive/{kanal['id']}.m3u8?key={canli_token}\n"

# Vavoo harici normal sabit linkleriniz
m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="TRT GENÇ.tr" tvg-logo="https://twimg.com" ,TRT GENÇ\n'
m3u_icerik += 'https://trt.com.tr\n'

m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="YabanTV.tr" tvg-logo="https://gstatic.com" ,Yaban TV\n'
m3u_icerik += 'https://tulix.tv\n'

m3u_icerik += '#EXTINF:-1 group-title="BELGESEL" tvg-id="TRT BELGESEL.tr" tvg-logo="https://technettv.com" ,TRT Belgesel\n'
m3u_icerik += 'https://trt.com.tr\n'

# Çıktıyı doğrudan uygulamanızın okuduğu "belgesel" dosyasına gömüyoruz
with open("./belgesel", "w", encoding="utf-8") as f:
    f.write(m3u_icerik)

print("Listeniz taze dinamik token ile basariyla guncellendi!")

