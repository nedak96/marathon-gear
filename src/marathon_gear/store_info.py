import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Any, cast

import boto3
from dataclasses_json import DataClassJsonMixin

# from botocore.exceptions import ClientError
from .constants import STORE_INFO_TABLE

if TYPE_CHECKING:
  from mypy_boto3_dynamodb.service_resource import Table
else:
  Table = object

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class StoreInfoProduct(DataClassJsonMixin):
  name: str
  price: Decimal
  url: str
  image: str


@dataclass
class StoreInfoDynamoRecord(DataClassJsonMixin):
  store: str
  products: list[StoreInfoProduct]


class StoreInfo:
  __table: Table
  __dynamorecord = StoreInfoDynamoRecord(store="", products=[])

  @property
  def products(self) -> list[StoreInfoProduct]:
    return self.__dynamorecord.products

  @property
  def table_key(self) -> dict[str, str]:
    return {"store": self.__dynamorecord.store}

  def __init__(self, store_key: str) -> None:
    self.__dynamorecord.store = store_key
    dynamodb = boto3.resource("dynamodb")
    self.__table = dynamodb.Table(STORE_INFO_TABLE)
    logger.info("Getting record: %s", self.__dynamorecord.store)
    try:
      item_resp = self.__table.get_item(Key=self.table_key)
    except Exception as e:
      logger.error("Error getting record")
      raise e

    if "Item" in item_resp:
      self.__dynamorecord = StoreInfoDynamoRecord.from_dict(item_resp["Item"])

  def update(self, products: list[StoreInfoProduct]) -> None:
    logger.info("Updating record: %s", self.__dynamorecord.store)
    try:
      self.__dynamorecord.products = products
      self.__table.put_item(Item=cast(dict[str, Any], self.__dynamorecord.to_dict()))
    except Exception as e:
      logger.error("Error updating record")
      raise e
