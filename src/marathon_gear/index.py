import logging
from email.mime.text import MIMEText

from aws_lambda_typing import context as context_
from aws_lambda_typing import events
from jinja2 import Template

from .constants import (
  GMAIL_ADDRESS,
  GMAIL_PASSWORD,
  NEW_BALANCE_KEY,
  NEW_BALANCE_URL,
  RECIPIENTS,
)
from .email import Email
from .scrape import Scrape
from .store_info import StoreInfo, StoreInfoProduct

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(_: events.EventBridgeEvent, context: context_.Context) -> None:
  logger.info("Starting lambda: %s", context.function_name)

  with Scrape() as scraper:
    products = scraper.get_products(NEW_BALANCE_URL)

  store_info = StoreInfo(NEW_BALANCE_KEY)

  new_products: list[StoreInfoProduct] = []
  price_drop_products: list[StoreInfoProduct] = []

  existing_products = {p.name: p for p in store_info.products}

  for p in products:
    if p.name not in existing_products:
      new_products.append(p)
    elif p.price < existing_products[p.name]:
      price_drop_products.append(p)

  if len(new_products) + len(price_drop_products) > 0:
    with open("./email_template.j2") as f:
      email_template = Template(f.read())
      email_cli = Email(GMAIL_ADDRESS, GMAIL_PASSWORD)
      msg = MIMEText(
        email_template.render(
          new_products=new_products,
          price_drop_products=price_drop_products,
          url=NEW_BALANCE_URL,
        ),
        "html",
      )
      msg["Subject"] = "Marathon gear updates"
      msg["From"] = "Marathon Gear Watcher"
      msg["To"] = ", ".join(RECIPIENTS)
      email_cli.send_email(
        RECIPIENTS,
        email_template.render(
          link=NEW_BALANCE_URL,
        ),
      )

  store_info.update(products)
