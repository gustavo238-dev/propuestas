import smtplib
from email.message import EmailMessage
from pathlib import Path

from src.shared.config.settings import settings


class SmtpEmailService:
    def send_html_email(
        self,
        recipients: list[str],
        subject: str,
        html_body: str,
        attachments: list[Path] | None = None,
    ) -> None:
        message = EmailMessage()
        message["From"] = settings.smtp_sender
        message["To"] = ", ".join(recipients)
        message["Subject"] = subject
        message.set_content("Este correo requiere un cliente compatible con HTML.")
        message.add_alternative(html_body, subtype="html")

        for attachment in attachments or []:
            message.add_attachment(
                attachment.read_bytes(),
                maintype="application",
                subtype="pdf",
                filename=attachment.name,
            )

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_user and settings.smtp_password:
                smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(message)
