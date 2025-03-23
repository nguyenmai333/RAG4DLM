import asyncio
from crawl4ai import *
import os
URL_BASE = 'https://hcmut.edu.vn/'

os.makedirs('data', exist_ok=True)

async def main():
    def pre_process(result):
        title = result.metadata.get('title')
        content = result.markdown
        with open(f'data/{title}.txt', 'w', encoding='utf-8') as f:
            f.write(content)
    # Define the base URL to crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=2, 
            include_external=False
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
        stream=True,
    )

    async with AsyncWebCrawler() as crawler:
        async for result in await crawler.arun(URL_BASE, config=config):
            pre_process(result)

if __name__ == "__main__":
    asyncio.run(main())