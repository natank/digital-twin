"""Email delivery abstraction."""

from src.email.sender import ConsoleEmailSender, EmailSender, get_email_sender

__all__ = ["ConsoleEmailSender", "EmailSender", "get_email_sender"]
