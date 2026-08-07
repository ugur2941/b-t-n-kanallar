import argparse
import asyncio
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from playwright.async_api import async_playwright

# --- VARSAYILAN YAPILANDIRMA ---
DEFAULT_CHANNEL_ID = "taraftarium"
DEFAULT_CHANNEL_NAME = "BeIN Sports 1"
DEFAULT_GROUP = "BeinSports"
DEFAULT_OUTPUT = "sporb"
DEFAULT_LOGO = "https://resmim.net/cdn/2026/07/22/ETtrXH.png"

# --- GITHUB HEDEF DEPO AYARLARI ---
GITHUB_REPO_OWNER = "ugur2941"
GITHUB_REPO_NAME = "b-t-n-kanallar"
GITHUB_FILE_PATH = "sporb"
GITHUB_BRANCH = "main"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
)

WHITESPACE_REGEX = re.compile(r"\s+")


def parse_args():
    parser = argparse.ArgumentParser(description="M3U8 Stream Extractor and GitHub Sync")
    parser.add_argument("--channel-id", default=DEFAULT_CHANNEL_ID, help="Kanal ID")
    parser.add_argument("--channel-name", default=DEFAULT_CHANNEL_NAME, help="Kanal Adı")
    parser.add_argument("--group", default=DEFAULT_GROUP, help="Kanal Grubu")
    parser.add_argument("--logo", default=DEFAULT_LOGO, help="Kanal Logosu URL")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Çıktı Dosya Adı")
    parser.add_argument("--github-token", default=os.getenv("GITHUB_TOKEN", ""), help="GitHub Personal Access Token")
    parser.add_argument("--start-domain", type=int, default=1000, help="Başlangıç Domain No")
    parser.add_argument("--end-domain", type=int, default=1600, help="Bitiş Domain No")
    return parser.parse_args()


def normalize_channel_name(value: str) -> str:
    return WHITESPACE_REGEX.sub(" ", value).strip().casefold()


def extract_channel_name(extinf_line: str) -> str | None:
    if not extinf_line.lstrip().startswith("#EXTINF") or "," not in extinf_line:
        return None
    return extinf_line.rsplit(",", 1)[-1].strip()


def upsert_playlist_entry(existing_content: str, channel_name: str, group: str, stream_url: str, domain: str, logo_url: str) -> str:
    lines = [line.strip() for line in existing_content.splitlines() if line.strip()]
    wanted_name = normalize_channel_name(channel_name)

    new_channel_block = [
        f'#EXTINF:-1 tvg-name="{channel_name}" tvg-logo="{logo_url}" group-title="{group}",{channel_name}',
        f'#EXTVLCOPT:http-user-agent={USER_AGENT}',
        f'#EXTVLCOPT:http-referrer={domain}',
        f'#EXT-X-USER-AGENT:{USER_AGENT}',
        f'#EXT-X-REFERER:{domain}',
        f'#EXT-X-ORIGIN:{domain}',
        stream_url
    ]

    header = "#EXTM3U"
    channels = []
    current_channel = []

    for line in lines:
        if line.startswith("#EXTM3U"):
            continue
        if line.startswith("#EXTINF"):
            if current_channel:
                channels.append(current_channel)
                current_channel = []
        current_channel.append(line)

    if current_channel:
        channels.append(current_channel)

    updated = False
    new_channels = []

    for ch_lines in channels:
        extinf_line = ch_lines[0]
        c_name = extract_channel_name(extinf_line)

        if c_name and normalize_channel_name(c_name) == wanted_name:
            new_channels.append(new_channel_block)
            updated = True
        else:
            new_channels.append(ch_lines)

    if not updated:
        new_channels.append(new_channel_block)

    output_lines = [header]
    for ch_lines in new_channels:
        output_lines.extend(ch_lines)

    return "\n".join(output_lines) + "\n"


async def find_working_domain(start=1000, end=1600):
    print("Calisan domain araniyor...\n")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=USER_AGENT)
        
        for num in range(start, end):
            test_url = f"https://taraftarium{num}.xyz"
            page = await context.new_page()
            try:
                response = await page.goto(test_url, timeout=4000, wait_until="commit")
                final_url = page.url
                
                if response and response.status < 400:
                    if final_url != test_url and not final_url.endswith("/"):
                        print(f"Deniyor -> taraftarium{num}.xyz redirect -> {final_url.split('/')[-1]}")
                    else:
                        print(f"Deniyor -> taraftarium{num}.xyz [BAŞARILI]")
                    
                    print("Yonlendirilen domain kabul edildi.")
                    await browser.close()
                    return final_url.rstrip("/")
            except Exception:
                pass
            finally:
                await page.close()
                
        await browser.close()
    return None


async def extract_m3u8(domain_url, channel_id="taraftarium"):
    urls_to_try = [
        f"{domain_url}/channel.html?id={channel_id}",
        f"{domain_url}/channel.html?id=1",
        f"{domain_url}/"
    ]

    captured_urls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-web-security"]
        )
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 720}
        )

        for target_page_url in urls_to_try:
            print(f"\nKanal sayfasina baglaniliyor: {target_page_url}")
            page = await context.new_page()

            def handle_request(request):
                url = request.url
                if ".m3u8" in url.lower() and "ads" not in url.lower():
                    print(f"[AĞDA YAKALANDI] -> {url}")
                    captured_urls.append(url)

            page.on("request", handle_request)

            try:
                await page.goto(target_page_url, timeout=15000, wait_until="domcontentloaded")
                await asyncio.sleep(3)

                # 1. Iframe adreslerini tara
                iframes = page.frames
                iframe_urls = [f.url for f in iframes if f.url and f.url != "about:blank"]
                
                for iframe_url in iframe_urls:
                    if "player" in iframe_url.lower() or "stream" in iframe_url.lower() or "channel" in iframe_url.lower():
                        print(f"[IFRAME TESPİT EDİLDİ] -> {iframe_url}")
                        try:
                            iframe_page = await context.new_page()
                            iframe_page.on("request", handle_request)
                            await iframe_page.goto(iframe_url, timeout=10000, wait_until="domcontentloaded")
                            await asyncio.sleep(4)
                            await iframe_page.close()
                        except Exception:
                            pass

                # 2. Sayfadaki tıklama alanlarını tetikle
                try:
                    await page.mouse.click(640, 360)
                    await asyncio.sleep(3)
                except Exception:
                    pass

                # 3. Sayfa kaynak kodunda HTML/JS içerisindeki m3u8 adreslerini ara
                content = await page.content()
                found_m3u8 = re.findall(r'https?://[^\s\'"]+\.m3u8[^\s\'"]*', content)
                for link in found_m3u8:
                    if "ads" not in link.lower() and link not in captured_urls:
                        print(f"[KAYNAK KODDA YAKALANDI] -> {link}")
                        captured_urls.append(link)

            except Exception as e:
                print(f"Sayfa yukleme uyarisi: {e}")
            finally:
                await page.close()

            if captured_urls:
                break

        await browser.close()

    if captured_urls:
        final_link = captured_urls[-1]
        
        if "/taraftarium/" in final_link.lower():
            print("[OTOMATİK DÜZELTME] Pasif 'taraftarium' yolu tespit edildi. Aktif 'patron' yoluna çevriliyor...")
            final_link = re.sub(r"/taraftarium/", "/patron/", final_link, flags=re.IGNORECASE)

        print(f"\n[ÇALIŞAN CANLI YAYIN LİNKİ YAKALANDI] -> {final_link}\n")
        return final_link
    
    return None


def push_to_github(github_token, stream_url, domain, channel_name, group_name, logo_url):
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Python-Script"
    }

    api_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/{GITHUB_FILE_PATH}"

    print(f"{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME} deposundan mevcut {GITHUB_FILE_PATH} dosyası çekiliyor...")
    
    req = urllib.request.Request(f"{api_url}?ref={GITHUB_BRANCH}", headers=headers)
    sha = None
    existing_content = ""

    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                file_json = json.loads(response.read().decode("utf-8"))
                sha = file_json.get("sha")
                existing_content = base64.b64decode(file_json["content"]).decode("utf-8")
                print(f"Mevcut {GITHUB_FILE_PATH} dosyası çekildi.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"{GITHUB_FILE_PATH} dosyası bulunamadı, yenisi oluşturulacak.")
        else:
            print(f"❌ GitHub API Okuma Hatası ({e.code}): {e.reason}")
            sys.exit(1)

    updated_content = upsert_playlist_entry(
        existing_content=existing_content,
        channel_name=channel_name,
        group=group_name,
        stream_url=stream_url,
        domain=domain,
        logo_url=logo_url
    )

    encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": f"Auto-update {channel_name} stream URL with logo",
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }
    if sha:
        payload["sha"] = sha

    print(f"{GITHUB_REPO_NAME} deposuna yeni commit gönderiliyor...")
    
    put_req = urllib.request.Request(
        api_url, 
        data=json.dumps(payload).encode("utf-8"), 
        headers=headers, 
        method="PUT"
    )

    try:
        with urllib.request.urlopen(put_req) as response:
            if response.status in [200, 201]:
                print(f"✅ GitHub başarıyla güncellendi! ({GITHUB_REPO_NAME}/{GITHUB_FILE_PATH})")
            else:
                print(f"❌ GitHub Hatası: Status {response.status}")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"❌ GitHub Commit Hatası ({e.code}): {e.reason}")
        sys.exit(1)


async def main():
    args = parse_args()

    print("Script baslatiliyor...\n")

    working_domain = await find_working_domain(start=args.start_domain, end=args.end_domain)
    if not working_domain:
        print("❌ Çalışan domain bulunamadı!")
        sys.exit(1)

    m3u8_url = await extract_m3u8(working_domain, channel_id=args.channel_id)
    if not m3u8_url:
        print("❌ M3U8 linki yakalanamadı!")
        sys.exit(1)

    github_token = args.github_token.strip()
    if not github_token:
        print("[UYARI] GitHub token verilmedi, işlem durduruldu.")
        sys.exit(1)

    push_to_github(
        github_token=github_token,
        stream_url=m3u8_url,
        domain=working_domain,
        channel_name=args.channel_name,
        group_name=args.group,
        logo_url=args.logo
    )


if __name__ == "__main__":
    asyncio.run(main())
