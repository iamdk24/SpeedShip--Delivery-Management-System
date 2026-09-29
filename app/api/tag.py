
from enum import Enum


class ApiTag(str, Enum):
    SHIPMENT="Shipment"
    SELLER="Seller"
    PARTNER="Partner"