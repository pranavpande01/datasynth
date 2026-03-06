import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import img2pdf

async def auto_scroll(page):
    await page.evaluate("""
        async () => {
            await new Promise((resolve) => {
                let total = 0;
                const step = 600;
                const timer = setInterval(() => {
                    window.scrollBy(0, step);
                    total += step;
                    if (total >= document.body.scrollHeight + 2000) {
                        clearInterval(timer);
                        resolve();
                    }
                }, 120);
            });
        }
    """)

async def url_to_pdf(url: str, out_pdf: str):
    out_pdf = str(Path(out_pdf))
    tmp_png = out_pdf.replace(".pdf", ".png")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            viewport={"width": 1366, "height": 2200},
            locale="en-US"
        )
        page = await context.new_page()
        page.set_default_navigation_timeout(90000)

        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)
        await auto_scroll(page)

        # Remove common overlays/popups
        await page.add_style_tag(content="""
            * { animation: none !important; transition: none !important; }
            [role="dialog"], .modal, .popup, .cookie, .consent, .subscribe, .newsletter {
                display: none !important;
                visibility: hidden !important;
            }
        """)

        await page.emulate_media(media="screen")

        try:
            await page.pdf(
                path=out_pdf,
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                margin={"top": "12mm", "bottom": "12mm", "left": "10mm", "right": "10mm"},
            )
        except Exception:
            await page.screenshot(path=tmp_png, full_page=True)
            with open(out_pdf, "wb") as f:
                f.write(img2pdf.convert(tmp_png))

        await browser.close()

asyncio.run(url_to_pdf("https://food.ndtv.com/food-drinks/the-best-street-food-hotspots-in-delhi-to-eat-like-a-local-9389184", "out.pdf"))
