import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


DEFAULT_CHANNEL_ID = "patron"
DEFAULT_CHANNEL_NAME = "BeIN Sports 1"
DEFAULT_GROUP = "BeinSports"
DEFAULT_OUTPUT = "sporb"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
)

REGEX_FALLBACK = re.compile(
    r"""["'](https?://[^"'\s]+?\.(?:sbs|xyz|com|net)/?[^"'\s]*?(?:mono|index|playlist)\.m3u8[^"'\s]*)["']""",
    re.IGNORECASE,
)
WHITESPACE_REGEX = re.compile(r"\s+")


def get_host(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host


def normalize_channel_name(value: str) -> str:
    return WHITESPACE_REGEX.sub(" ", value).strip().casefold()


def extract_channel_name(extinf_line: str) -> str | None:
    if not extinf_line.lstrip().startswith("#EXTINF") or "," not in extinf_line:
        return None
    return extinf_line.rsplit(",", 1)[-1].strip()


def upsert_playlist_entry(existing_content: str, channel_name: str, group: str, stream_url: str, domain: str) -> str:
    """
    Eski M3U dosyasındaki diğer kanalları korur. 
    Güncellenmek istenen kanal varsa sadece onu ve altındaki başlıkları değiştirir.
    Yoksa listenin en altına ekler.
    """
    lines = existing_content.splitlines()
    wanted_name = normalize_channel_name(channel_name)
    
    new_block = [
        f'#EXTVLCOPT:http-user-agent={USER_AGENT}',
        f'#EXTVLCOPT:http-referrer={domain}',
        f'#EXT-X-USER-AGENT:{USER_AGENT}',
        f'#EXT-X-REFERER:{domain}',
        f'#EXT-X-ORIGIN:{domain}',
        stream_url
    ]

    target_index = -1
    for index, line in enumerate(lines):
        current_name = extract_channel_name(line)
        if current_name and normalize_channel_name(current_name) == wanted_name:
            target_index = index
            break

    if target_index != -1:
        # Mevcut kanalı bulduk. Altındaki eski link ve #EXTVLCOPT / #EXT-X satırlarını temizliyoruz.
        end_index = target_index + 1
        while end_index < len(lines):
            next_line = lines[end_index].strip()
            if not next_line:
                end_index += 1
                continue
            if next_line.startswith("#EXTINF"):
                break
            if next_line.startswith("#") or next_line.startswith("http"):
                end_index += 1
            else:
                break
        
        # Eski bloğu silip yerine yeni proxy başlıklarını ve linki yerleştiriyoruz
        lines[target_index + 1:end_index] = new_block
    else:
        # Kanal listede yoksa, yeni bir #EXTINF satırıyla birlikte en alta ekliyoruz
        if lines and not lines[-1].strip():
            lines.pop()
        lines.append(f'#EXTINF:-1 tvg-name="{channel_name}" group-title="{group}",{channel_name}')
        lines.extend(new_block)

    final_lines = []
    if lines and not lines[0].startswith("#EXTM3U"):
        final_lines.append("#EXTM3U")
    
    for l in lines:
        if l.startswith("#EXTM3U") and final_lines:
            continue
        final_lines.append(l)

    return "\n".join(final_lines).rstrip() + "\n"


def write_output(output_path: str, channel_name: str, group: str, stream_url: str, domain: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        existing_content = path.read_text(encoding="utf-8")
        # Eski kanalları koruyarak güncelleme yapıyoruz
        final_content = upsert_playlist_entry(existing_content, channel_name, group, stream_url, domain)
    else:
        # Dosya hiç yoksa sıfırdan oluştur
        final_content = "#EXTM3U\n" + (
            f'#EXTINF:-1 tvg-name="{channel_name}" group-title="{group}",{channel_name}\n'
            f'#EXTVLCOPT:http-user-agent={USER_AGENT}\n'
            f'#EXTVLCOPT:http-referrer={domain}\n'
            f'#EXT-X-USER-AGENT:{USER_AGENT}\n'
            f'#EXT-X-REFERER:{domain}\n'
            f'#EXT-X-ORIGIN:{domain}\n'
            f'{stream_url}\n'
        )

    path.write_text(final_content, encoding="utf-8")


def find_working_domain(context, start_num: int, end_num: int, blocked_hosts: set[str]) -> str | None:
    print("\nCalisan domain araniyor...\n")

    for num in range(start_num, end_num + 1):
        expected_host = f"taraftarium{num}.xyz"
        test_url = f"https://{expected_host}/"
        print(f"Deniyor -> {expected_host}", end=" ")

        page = context.new_page()
        try:
            response = page.goto(test_url, timeout=12000, wait_until="domcontentloaded")
            final_host = get_host(page.url.rstrip("/"))

            if final_host != expected_host:
                print(f"redirect -> {final_host}")
                if "taraftarium" in final_host and final_host.endswith(".xyz"):
                    print("Yonlendirilen domain kabul edildi.")
                    return f"https://{final_host}"
                continue

            if final_host in blocked_hosts:
                print("engelli host")
                continue

            if not response or not response.ok:
                print(f"HTTP {response.status if response else 'cevap yok'}")
                continue

            title = page.title().lower()
            if any(x in title for x in ["cloudflare", "just a moment", "attention"]):
                print("koruma sayfasi algilandi, 5 sn bekleniyor...")
                page.wait_for_timeout(5000)
                title = page.title().lower()
                if any(x in title for x in ["cloudflare", "just a moment"]):
                    print("koruma gecilemedi.")
                    continue

            print("tamam")
            return f"https://{expected_host}"
        except Exception as e:
            print(f"hata -> {str(e)[:80]}")
        finally:
            page.close()
            time.sleep(1.0)

    print("\nCalisan domain bulunamadi.")
    return None


def resolve_channel_stream(context, domain: str, channel_id: str) -> str | None:
    page = context.new_page()
    url = f"{domain.rstrip('/')}/channel.html?id={channel_id}"
    captured_m3u8 = None

    def handle_request(request):
        nonlocal captured_m3u8
        req_url = request.url.lower()
        if ".m3u8" in req_url and any(x in req_url for x in ["mono", "index", "playlist"]):
            captured_m3u8 = request.url

    page.on("request", handle_request)

    try:
        page.goto(url, timeout=18000, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        for selector in ["body", "iframe", "div#player"]:
            try:
                page.click(selector, timeout=2000)
                page.wait_for_timeout(1000)
            except Exception:
                pass

        start_time = time.time()
        while time.time() - start_time < 12:
            if captured_m3u8:
                return captured_m3u8
            page.wait_for_timeout(700)

        content = page.content()
        match = REGEX_FALLBACK.search(content)
        if match:
            return match.group(1)

        return None
    finally:
        page.remove_listener("request", handle_request)
        page.close()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel-id", default=DEFAULT_CHANNEL_ID)
    parser.add_argument("--channel-name", default=DEFAULT_CHANNEL_NAME)
    parser.add_argument("--group", default=DEFAULT_GROUP)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--start-domain", type=int, default=1061)
    parser.add_argument("--end-domain", type=int, default=1500)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    blocked_hosts = {"taraftariumgir.is"}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--autoplay-policy=no-user-gesture-required",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )

        context = browser.new_context(
            user_agent=USER_AGENT,
            ignore_https_errors=True,
            viewport={"width": 1366, "height": 768},
        )

        try:
            domain = find_working_domain(context, args.start_domain, args.end_domain, blocked_hosts)
            if not domain:
                print("Uyarici: Calisan domain bulunamadi!")
                return 1

            print(f"Kullanilan dinamik domain: {domain}")
            stream_url = resolve_channel_stream(context, domain, args.channel_id)
            if not stream_url:
                print("m3u8 linki sayfa icerisinde yakalanamadi.")
                return 1

            write_output(
                output_path=args.output,
                channel_name=args.channel_name,
                group=args.group,
                stream_url=stream_url,
                domain=domain
            )

            print(f"Tamamlandi -> {args.output}")
            return 0
        finally:
            browser.close()


if __name__ == "__main__":
    sys.exit(main())
