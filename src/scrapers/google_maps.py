import asyncio
from typing import AsyncGenerator, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from src.scrapers.base import BaseScraper
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GoogleMapsScraper(BaseScraper):
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Browser = None
        
    async def _init_browser(self):
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            
    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def scrape(self, query: str, max_results: int = 50) -> AsyncGenerator[Dict[str, Any], None]:
        await self._init_browser()
        context = await self.browser.new_context(locale="en-US")
        page = await context.new_page()
        
        try:
            import urllib.parse
            safe_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/maps/search/{safe_query}"
            logger.info(f"Navigating to Google Maps search: {search_url}")
            await page.goto(search_url)
            
            # Attempt to bypass EU/UK cookie consent if it appears
            try:
                consent_button = page.locator('button:has-text("Accept all")')
                if await consent_button.count() > 0:
                    await consent_button.first.click()
                    await asyncio.sleep(2)
            except Exception:
                pass
            
            # Wait for search results
            await page.wait_for_selector('a[href*="/maps/place/"]', timeout=15000)
            
            # Scroll to load items
            yielded_urls = set()
            scroll_count = 0
            max_scrolls = 20
            
            while len(yielded_urls) < max_results and scroll_count < max_scrolls:
                items = await page.locator('a[href*="/maps/place/"]').all()
                new_items_found = False
                
                for item in items:
                    href = await item.get_attribute("href")
                    if href and href not in yielded_urls and len(yielded_urls) < max_results:
                        new_items_found = True
                        yielded_urls.add(href)
                        detail_url = href
                        
                        # We yield partial dict and fetch details by navigating to detail_url in a separate tab or using data from summary
                        # For a robust scraper, it's better to extract what we can without clicking, or navigate directly
                        try:
                            # It's safer to open a new tab for details so we don't lose scroll state
                            detail_data = await self._scrape_detail(context, detail_url)
                            if detail_data:
                                yield detail_data
                        except Exception as e:
                            logger.error(f"Error extracting details: {e}")
                            
                if not new_items_found:
                    break
                    
                # Scroll
                scroll_count += 1
                sidebar = page.locator('div[role="feed"]')
                if await sidebar.count() > 0:
                    await sidebar.hover()
                    await page.mouse.wheel(0, 5000)
                    await asyncio.sleep(2)
                else:
                    break
                    
        except Exception as e:
            logger.error(f"Scraping failed for query '{query}': {e}")
        finally:
            await page.close()
            await context.close()

    async def _scrape_detail(self, context, url: str) -> Dict[str, Any]:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2) # Allow React app to populate fields
            
            # Extract basic info
            name_locator = page.locator('h1').first
            name = await name_locator.inner_text() if await name_locator.count() > 0 else ""
            
            # Category
            category_loc = page.locator('button[jsaction*="category"]').first
            category = await category_loc.inner_text() if await category_loc.count() > 0 else ""
            
            # Phone number
            phone_loc = page.locator('button[data-tooltip*="phone number"] div.fontBodyMedium').first
            phone = await phone_loc.inner_text() if await phone_loc.count() > 0 else ""
            
            # Website
            website_loc = page.locator('a[data-tooltip*="website"]').first
            website = await website_loc.get_attribute("href") if await website_loc.count() > 0 else ""
            
            # Address
            address_loc = page.locator('button[data-tooltip*="address"] div.fontBodyMedium').first
            address = await address_loc.inner_text() if await address_loc.count() > 0 else ""
            
            return {
                "business_name": name,
                "category": category,
                "phone_number": phone,
                "website": website,
                "address": address,
                "url": url
            }
        finally:
            await page.close()
