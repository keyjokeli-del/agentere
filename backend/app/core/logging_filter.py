import re
import logging
from typing import Any

# Regex patterns for sensitive PII
PHONE_REGEX = re.compile(r'(\+?\d{1,3}[\s\-]?)?(\d{2,4})[\s\-]?\d{3,4}[\s\-]?(\d{3,4})')
WHATSAPP_JID_REGEX = re.compile(r'(\d{4})\d{4,8}(\d{4})(@s\.whatsapp\.net)')
EMAIL_REGEX = re.compile(r'([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]{2,}@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')


def mask_pii(text: str) -> str:
    """Masks phone numbers, emails and WhatsApp JIDs in a string."""
    if not isinstance(text, str):
        return text

    # Mask WhatsApp JIDs first
    text = WHATSAPP_JID_REGEX.sub(r'\1****\2\3', text)

    # Mask standard phone numbers (leaving prefix and last 3 digits)
    def phone_repl(match):
        full = match.group(0)
        if len(full) < 7:
            return full
        return full[:4] + "****" + full[-3:]

    text = PHONE_REGEX.sub(phone_repl, text)

    # Mask emails
    text = EMAIL_REGEX.sub(r'\1***@\2', text)

    return text


class PIIMaskingFilter(logging.Filter):
    """Logging filter that redacts PII before messages are output to console/logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            if isinstance(record.msg, str):
                record.msg = mask_pii(record.msg)
            if record.args:
                if isinstance(record.args, dict):
                    record.args = {k: mask_pii(v) if isinstance(v, str) else v for k, v in record.args.items()}
                elif isinstance(record.args, tuple):
                    record.args = tuple(mask_pii(arg) if isinstance(arg, str) else arg for arg in record.args)
        except Exception:
            pass
        return True


def setup_pii_logging():
    """Attaches PIIMaskingFilter to root, uvicorn and app loggers."""
    pii_filter = PIIMaskingFilter()
    root_logger = logging.getLogger()
    root_logger.addFilter(pii_filter)

    for handler in root_logger.handlers:
        handler.addFilter(pii_filter)

    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "app", "fastapi"]:
        l = logging.getLogger(logger_name)
        l.addFilter(pii_filter)
        for h in l.handlers:
            h.addFilter(pii_filter)
