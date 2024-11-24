import logging
import re
from decimal import Decimal
from os import environ
from typing import Callable, Literal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from .store_info import StoreInfoProduct

logger = logging.getLogger()
logger.setLevel(logging.INFO)
environ.update(SE_AVOID_STATS="true")

VIEWED_PRODUCTS_REGEX = re.compile("(\\d+) of \\d+")


class Scrape:
  __driver: WebDriver

  def __init__(self, binary_path="/opt"):
    service = webdriver.ChromeService(
      executable_path=f"{binary_path}/chromedriver-linux64/chromedriver",
    )
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(
      "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    )
    options.binary_location = f"{binary_path}/chrome-linux64/chrome"
    self.__driver = webdriver.Chrome(options=options, service=service)
    self.__driver.implicitly_wait(30)

  def __enter__(self):
    return self

  def __exit__(self, *_):
    self.__driver.quit()

  @staticmethod
  def get_text(el: WebElement, attr="innerText") -> str:
    return (el.get_attribute(attr) or "").strip()

  def get_viewed_products(self, driver: WebDriver) -> str:
    viewed_txt = self.get_text(driver.find_element(By.CLASS_NAME, "products-viewed"))
    viewed_count_txt = VIEWED_PRODUCTS_REGEX.search(viewed_txt)
    if viewed_count_txt is None:
      raise Exception("Error getting viewed count")
    return viewed_count_txt.group(1)

  def create_wait_for_update(
    self,
    current_viewed: str,
  ) -> Callable[[WebDriver], bool | Literal[False]]:
    def create_for_update(driver: WebDriver) -> bool | Literal[False]:
      return self.get_viewed_products(driver) != current_viewed

    return create_for_update

  def get_products(self, url: str) -> list[StoreInfoProduct]:
    logger.info("Scraping URL: %s", url)
    self.__driver.get(url)
    num_products = self.get_text(self.__driver.find_element(By.CLASS_NAME, "pgp-count"))
    logger.info("Found number of products: %s", num_products)
    while True:
      viewed_count = self.get_viewed_products(self.__driver)
      logger.info("Found view count: %s", viewed_count)
      if viewed_count == num_products:
        break
      btn = self.__driver.find_element(By.ID, "btn-loadMore")
      self.__driver.execute_script("arguments[0].click();", btn)
      WebDriverWait(self.__driver, 30).until(self.create_wait_for_update(viewed_count))

    logger.info("Getting product details")
    products: list[StoreInfoProduct] = []
    product_els = self.__driver.find_elements(By.CLASS_NAME, "product")
    for product_el in product_els:
      products.append(
        StoreInfoProduct(
          name=self.get_text(product_el, "aria-label"),
          price=Decimal(
            self.get_text(product_el.find_element(By.CLASS_NAME, "sales")).strip("$"),
          ),
          url=self.get_text(
            product_el.find_element(By.TAG_NAME, "a"),
            "href",
          ).split("?")[0],
          image=self.get_text(
            product_el.find_element(By.CSS_SELECTOR, ".tile-image[data-src]"),
            "data-src",
          ).split("?")[0],
        ),
      )
    return products
