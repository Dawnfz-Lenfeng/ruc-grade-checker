import logging

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, send_key):
        self.send_key = send_key
        self.api_url = f"https://sctapi.ftqq.com/{send_key}.send"

    def send_notification(self, title, message):
        try:
            data = {"title": title, "desp": message}
            response = requests.post(self.api_url, data=data)
            response.raise_for_status()
            logger.info("Successfully sent notification")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
