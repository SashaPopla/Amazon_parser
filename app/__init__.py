import os
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