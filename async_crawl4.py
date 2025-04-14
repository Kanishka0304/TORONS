import asyncio
import aiohttp
from bs4 import BeautifulSoup
from multiprocessing import Process
from urllib.parse import urljoin, urlencode
from colorama import Fore, init

init()

# CONFIG
KEYWORDS = ["index", "heroin", "meth"]
SEARCH_ENGINE = "https://html.duckduckgo.com/html/"
MAX_DEPTH = 4  # DuckDuckGo pages usually don't allow deep crawling


def print_colored(text, color):
    print(color + text + Fore.RESET)


async def fetch_and_extract_links(url, session):
    try:
        async with session.get(url, timeout=15) as response:
            if response.status != 200:
                print_colored(f"Failed: {url} ({response.status})", Fore.RED)
                return []
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
            links = [
                urljoin(str(response.url), a['href'])
                for a in soup.find_all('a', href=True)
                if not a['href'].startswith('mailto:')
            ]
            print_colored(f"[+] Crawled: {url} -> Found {len(links)} links", Fore.GREEN)
            return links
    except Exception as e:
        print_colored(f"[!] Error: {url} ({e})", Fore.RED)
        return []


async def crawl_recursive(start_url, session, depth=1, max_depth=1):
    if depth > max_depth:
        return
    links = await fetch_and_extract_links(start_url, session)
    tasks = [
        crawl_recursive(link, session, depth + 1, max_depth)
        for link in links
    ]
    await asyncio.gather(*tasks)


async def keyword_crawler(keyword):
    params = {'q': keyword}
    search_url = f"{SEARCH_ENGINE}{keyword}"

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Crawler/1.0)"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        print_colored(f"[Keyword: {keyword}] Crawling: {search_url}", Fore.CYAN)
        await crawl_recursive(search_url, session, max_depth=MAX_DEPTH)


def run_keyword_crawler(keyword):
    asyncio.run(keyword_crawler(keyword))


def start_multiprocess_crawlers():
    print_colored(f"[+] Starting crawlers for {len(KEYWORDS)} keywords...", Fore.YELLOW)
    processes = []
    for keyword in KEYWORDS:
        p = Process(target=run_keyword_crawler, args=(keyword,))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


if __name__ == "__main__":
    start_multiprocess_crawlers()

