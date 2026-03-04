from crawl4ai import AsyncWebCrawler
import asyncio

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://lbb.in/delhi/budget-alcohol-bars-delhi/"
        )

        print(result.title)
        print(result.markdown)
        print(result.links)

asyncio.run(main())