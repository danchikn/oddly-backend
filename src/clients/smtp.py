from loguru import logger
from email.message import EmailMessage

import aiosmtplib

from src.core.config import settings



class SmtpClient:
    def __init__(self) -> None:
        self._host = settings.SMTP_HOST
        self._port = settings.SMTP_PORT
        self._username = settings.SMTP_USER
        self._password = settings.SMTP_PASSWORD
        self._from = settings.SMTP_FROM

    async def send_email(self, to: str, subject: str, body: str) -> None:
        if not self._username or not self._password:
            logger.warning('SMTP not configured — logging email instead')
            logger.info('=== EMAIL ===\nTo: %s\nSubject: %s\n%s\n=============', to, subject, body)
            return

        msg = EmailMessage()
        msg['From'] = self._from
        msg['To'] = to
        msg['Subject'] = subject
        msg.set_content(body)

        try:
            await aiosmtplib.send(
                msg,
                hostname=self._host,
                port=self._port,
                username=self._username,
                password=self._password,
                start_tls=True,
            )
            logger.info('Email sent: to=%s, subject=%s', to, subject)
        except Exception:
            logger.warning('SMTP failed — logging email instead: to=%s, subject=%s', to, subject, exc_info=True)
            logger.info('=== EMAIL ===\nTo: %s\nSubject: %s\n%s\n=============', to, subject, body)
