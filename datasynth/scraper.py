import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    # Use the context manager to wrap the playwright instance
    async with Stealth().use_async(async_playwright()) as p:
        # Launch browser (headless=False helps bypass tougher blocks)
        browser = await p.chromium.launch(headless=False)
        
        # Create a page (stealth is automatically applied here)
        page = await browser.new_page()

        # Navigate to the target site
        await page.goto("https://food.ndtv.com/food-drinks/the-best-street-food-hotspots-in-delhi-to-eat-like-a-local-9389184", wait_until="networkidle")

        # Generate your PDF
        await page.pdf(path="stealth_output.pdf", format="A4", print_background=True)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
