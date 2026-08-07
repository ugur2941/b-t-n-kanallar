import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Standart tarayıcı başlatma
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Ağ üzerinden geçen istekleri dinleme
        def on_request(request):
            # Örnek: Yalnızca belirli uzantılara veya API çağrılarına odaklanma
            if ".m3u8" in request.url or ".mpd" in request.url:
                print(f"[YAKALANAN MEDYA İSTEĞİ]: {request.url}")

        page.on("request", on_request)

        # Hedef sayfaya gitme
        print("Sayfa yükleniyor...")
        try:
            await page.goto("https://example.com", timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(5)  # Dinamik içeriklerin yüklenmesi için bekleme
        except Exception as e:
            print(f"Yükleme hatası: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
