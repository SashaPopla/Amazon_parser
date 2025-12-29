import time
import random
import re
import os
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class AmazonParser:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox") 
        self.options.add_argument("--disable-dev-shm-usage")

        chrome_bin = os.environ.get("CHROME_BIN")
        if chrome_bin:
            self.options.binary_location = chrome_bin

        self.service = Service(ChromeDriverManager().install())
        self.driver = None

        self.service = Service(ChromeDriverManager().install())
        self.driver = None

    def start_browser(self):
        if not self.driver:
            self.driver = webdriver.Chrome(service=self.service, options=self.options)

    def close_browser(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def get_detailed_product(self, url, rank):
        print(f"   -> Парсинг товару #{rank}...")
        self.driver.get(url)
        time.sleep(random.uniform(2, 4))
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        asin = "N/A"
        if '/dp/' in url:
            try:
                asin = url.split('/dp/')[1].split('/')[0]
            except: pass

        title_tag = soup.select_one('#productTitle')
        title = title_tag.text.strip() if title_tag else "Unknown Title"

        price = "N/A"
        
        price_selectors = [
            '.priceToPay span.a-offscreen',
            '.a-price.aok-align-center .a-offscreen',
            '.a-price .a-offscreen',
            'span.a-price-whole',
            '#priceblock_ourprice',
            '#priceblock_dealprice',
            '#corePrice_feature_div .a-offscreen',
            '#corePriceDisplay_desktop_feature_div .a-offscreen',
            'span#price',
        ]

        for selector in price_selectors:
            tag = soup.select_one(selector)
            if tag:
                txt = tag.text.strip()
                if any(c.isdigit() for c in txt):
                    price = txt
                    if selector == 'span.a-price-whole' and '$' not in price:
                        price = '$' + price
                    break

        if price == "N/A":
            print(f"      [DEBUG] Селектори не знайшли ціну. Шукаю в тексті...")
            text_content = soup.get_text()
            match = re.search(r'\$[\d,]+\.\d{2}', text_content)
            if match:
                price = match.group(0)
                print(f"      [DEBUG] Знайдено Regex-ом: {price}")
            else:
                match_int = re.search(r'\$[\d,]+', text_content)
                if match_int:
                    price = match_int.group(0)

        list_price = None
        list_price_tag = soup.select_one('.a-price.a-text-price span.a-offscreen')
        if list_price_tag: list_price = list_price_tag.text.strip()

        discount = None
        discount_tag = soup.select_one('.savingsPercentage') or soup.select_one('#regularprice_savings_percentage')
        if discount_tag: discount = discount_tag.text.strip()

        is_prime = False
        if soup.select_one('#prime-header-icon') or soup.select_one('.texgyreheros-regular'):
             is_prime = True

        rating = "0"
        rating_tag = soup.select_one('#acrPopover')
        if rating_tag:
            rt = rating_tag.get('title', '')
            if 'out of' in rt: rating = rt.split(' ')[0]
        
        reviews = "0"
        reviews_tag = soup.select_one('#acrCustomerReviewText')
        if reviews_tag: reviews = reviews_tag.text.split(' ')[0]

        bullets = []
        for b in soup.select('#feature-bullets li span.a-list-item'):
            txt = b.text.strip()
            if txt and len(bullets) < 5: bullets.append(txt)

        bsr = "N/A"
        bsr_match = re.search(r'#([0-9,]+)\s+in\s', soup.get_text())
        if bsr_match: bsr = f"#{bsr_match.group(1)}"

        img_url = ""
        img_tag = soup.select_one('#landingImage') or soup.select_one('#imgBlkFront')
        if img_tag: img_url = img_tag.get('src', '')

        return {
            "asin": asin,
            "title": title,
            "rank": rank,
            "price": price,
            "list_price": list_price,
            "discount_percent": discount,
            "rating": rating,
            "reviews_count": reviews,
            "is_prime": is_prime,
            "best_sellers_rank": bsr,
            "bullet_points": bullets,
            "main_image_url": img_url,
            "product_url": url,
            "currency": "$" if "$" in price else "USD"
        }

    def parse_category(self, url):
        self.start_browser()
        print(f"Відкриваю категорію: {url}")
        try:
            self.driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            product_urls = []
            seen = set()
            for link in soup.select('.zg-grid-general-faceout a.a-link-normal'):
                href = link.get('href')
                if href and '/dp/' in href:
                    full = "https://www.amazon.com" + href.split('/ref=')[0]
                    if full not in seen:
                        product_urls.append(full)
                        seen.add(full)
                if len(product_urls) >= 5: break
            
            print(f"Знайдено {len(product_urls)} товарів. Збір деталей...")
            
            final = []
            for i, u in enumerate(product_urls, 1):
                try:
                    final.append(self.get_detailed_product(u, i))
                except Exception as e:
                    print(f"Помилка {i}: {e}")
            return final
        except Exception as e:
            print(f"Error: {e}")
            return []
        finally:
            self.close_browser()