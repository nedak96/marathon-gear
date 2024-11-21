import logging
import smtplib

from .constants import (
  GMAIL_SERVER,
  GMAIL_SERVER_PORT,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Email:
  __username: str
  __password: str

  def __init__(self, username: str, password: str):
    self.__username = username
    self.__password = password

  def send_email(self, recipients: list[str], text: str) -> None:
    try:
      with smtplib.SMTP_SSL(
        GMAIL_SERVER,
        port=GMAIL_SERVER_PORT,
      ) as server:
        server.login(self.__username, self.__password)
        # msg = MIMEText()
        # msg["Subject"] = ""
        # msg["From"] = ""
        # msg[]
        server.sendmail(
          self.__username,
          recipients,
          text,
        )
    except Exception as e:
      logger.error("Error sending email: %s", e)
      raise e
