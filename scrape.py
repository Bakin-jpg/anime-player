import sys
import json
import asyncio
import re
from datetime import datetime
from playwright.async_api import async_playwright

async def scrape_video(url: str):
    result = {
        "timestamp": datetime.utcnow().isoformat(), "success": False, "url": url,
        "iframe_url": None, "page_title": None, "error": None
    }
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = await browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            page = await context.new_page()
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            result['page_title'] = await page.title()
            
            iframe_url = None
            try:
                iframe_handle = await page.wait_for_selector('iframe', timeout=15000)
                iframe_url = await iframe_handle.get_attribute('src')
            except Exception:
                content = await page.content()
                matches = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', content)
                if matches:
                    iframe_url = matches[0]

            await browser.close()
            
            if iframe_url:
                if not iframe_url.startswith('http'):
                    from urllib.parse import urljoin
                    iframe_url = urljoin(url, iframe_url)
                result['success'] = True
                result['iframe_url'] = iframe_url
            else:
                result['error'] = "Tidak dapat menemukan iframe."
    except Exception as e:
        result['error'] = str(e)
    return result

if __name__ == "__main__":
    video_url = sys.argv[1]
    result = asyncio.run(scrape_video(video_url))
    with open('result.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result['success'] else 1)
