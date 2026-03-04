import logging

logger = logging.getLogger(__name__)


def send_notification(user_tokens: list[str], title: str, body: str) -> None:
    logger.info("Log-only notification | tokens=%s | title=%s | body=%s", user_tokens, title, body)
