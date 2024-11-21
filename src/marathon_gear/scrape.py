import re
from os import environ
from typing import Callable, Literal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from .constants import IS_LOCAL
from .store_info import StoreInfoProduct

environ.update(SE_AVOID_STATS="true")

VIEWED_PRODUCTS_REGEX = re.compile("(\d+) of \d+")


class Scrape:
  __driver: WebDriver

  def __init__(self):
    service = webdriver.ChromeService()
    options = webdriver.ChromeOptions()
    if not IS_LOCAL:
      service = webdriver.ChromeService(executable_path="/opt/chromedriver")
      options.binary_location = "/opt/headless-chromium"
      options.add_argument("--headless")
      options.add_argument("--no-sandbox")
      options.add_argument("--single-process")
      options.add_argument("--disable-dev-shm-usage")
    self.__driver = webdriver.Chrome(options=options, service=service)
    self.__driver.implicitly_wait(30)

  def __enter__(self):
    return self

  def __exit__(self, *_):
    self.__driver.quit()

  @staticmethod
  def get_viewed_products(driver: WebDriver) -> str:
    viewed_txt = driver.find_element(By.CLASS_NAME, "products-viewed").get_attribute(
      "innerText",
    )
    viewed_count_txt = VIEWED_PRODUCTS_REGEX.search(viewed_txt or "")
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
    self.__driver.get(url)
    num_products = self.__driver.find_element(By.CLASS_NAME, "pgp-count").text.strip()
    while True:
      viewed_count = self.get_viewed_products(self.__driver)
      if viewed_count == num_products:
        break
      btn = self.__driver.find_element(By.ID, "btn-loadMore")
      self.__driver.execute_script("arguments[0].click();", btn)
      WebDriverWait(self.__driver, 30).until(self.create_wait_for_update(viewed_count))

    products: list[StoreInfoProduct] = []
    product_els = self.__driver.find_elements(By.CLASS_NAME, "product")
    for product_el in product_els:
      products.append(
        StoreInfoProduct(
          name=(product_el.get_attribute("aria-label") or ""),
          price=float(
            product_el.find_element(By.CLASS_NAME, "sales").text.strip().strip("$"),
          ),
          url=(
            product_el.find_element(By.TAG_NAME, "a").get_attribute("href") or ""
          ).split("?")[0],
          image=(
            product_el.find_element(
              By.CSS_SELECTOR,
              ".tile-image[data-src]",
            ).get_attribute("data-src")
            or ""
          ).split("?")[0],
        ),
      )
    return products
