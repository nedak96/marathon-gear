import os

IS_LOCAL = os.getenv("AWS_LAMBDA_FUNCTION_NAME") is None

GMAIL_SERVER = "smtp.gmail.com"
GMAIL_SERVER_PORT = 465
GMAIL_ADDRESS = os.environ["GMAIL_ADDRESS"]
GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]

STORE_INFO_TABLE = os.environ["STORE_INFO_TABLE"]
NEW_BALANCE_URL = "https://www.joesnewbalanceoutlet.com/search/?q=marathon"
NEW_BALANCE_KEY = "joesnewbalanceoutlet"

RECIPIENTS = os.environ["RECIPIENTS"].split(",")
