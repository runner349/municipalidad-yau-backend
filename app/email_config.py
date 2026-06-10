from fastapi_mail import ConnectionConfig
from .config import settings

# Nueva configuración (funciona en Render)
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.SMTP_USER,
    MAIL_PORT=465,                  # Puerto SSL
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=False,            # No usar STARTTLS
    MAIL_SSL_TLS=True,              # Usar SSL directo
    USE_CREDENTIALS=True,
)