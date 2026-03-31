import argparse
import logging
import os
import re
import time
from contextlib import suppress
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

INBOX_URL = "https://e.mail.ru/inbox"
DEFAULT_PROFILE_PATH = r"C:\ChromeProfiles\MailRuAutomation"
LETTER_XPATH = "//a[.//span[contains(text(), 'Instagram code') or contains(text(), 'is your Instagram code')]]"
CODE_PATTERN = re.compile(r"\b(\d{6})\b")


class MailRuCodeFetcher:
    def __init__(self, profile_path: str = DEFAULT_PROFILE_PATH, keep_open: bool = False):
        self.profile_path = Path(profile_path)
        self.keep_open = keep_open
        self.driver = None

    def _build_driver(self):
        self.profile_path.mkdir(parents=True, exist_ok=True)

        options = Options()
        options.add_argument(f"--user-data-dir={self.profile_path}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    @staticmethod
    def _extract_code(text: str):
        match = CODE_PATTERN.search(text or "")
        return match.group(1) if match else None

    def fetch_code(self, timeout: int = 90, refresh_interval: int = 5):
        if self.driver is None:
            self._build_driver()

        self.driver.get(INBOX_URL)
        logger.info("Mail.ru inbox opened. Waiting for Instagram letter...")

        deadline = time.time() + timeout
        while time.time() < deadline:
            with suppress(Exception):
                self.driver.refresh()

            try:
                letter = WebDriverWait(self.driver, 8).until(
                    EC.element_to_be_clickable((By.XPATH, LETTER_XPATH))
                )
                code = self._extract_code(letter.text)
                if code:
                    logger.info("Instagram code found: %s", code)
                    return code
            except TimeoutException:
                logger.debug("Letter not found on this attempt")

            time.sleep(max(1, refresh_interval))

        logger.warning("Timed out waiting for Instagram code")
        return None

    def close(self):
        if self.driver and not self.keep_open:
            self.driver.quit()
            self.driver = None


def get_instagram_code(profile_path: str = DEFAULT_PROFILE_PATH, timeout: int = 90, refresh_interval: int = 5):
    fetcher = MailRuCodeFetcher(profile_path=profile_path)
    try:
        return fetcher.fetch_code(timeout=timeout, refresh_interval=refresh_interval)
    finally:
        fetcher.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Get Instagram confirmation code from Mail.ru")
    parser.add_argument("--profile-path", default=DEFAULT_PROFILE_PATH)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--refresh-interval", type=int, default=5)
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level), format="%(asctime)s [%(levelname)s] %(message)s")

    code = get_instagram_code(
        profile_path=args.profile_path,
        timeout=args.timeout,
        refresh_interval=args.refresh_interval,
    )

    if code:
        print(code)
        return 0

    print("Code not found")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
