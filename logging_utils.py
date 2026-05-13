import json
import logging
from datetime import datetime, timezone


class JsonLogFormatter(logging.Formatter):
    """Structured JSON formatter for application logs."""

    def format(self, record):
        payload = {
            'ts': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        if record.exc_info:
            payload['exc'] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


def configure_logging(level='INFO'):
    """Configure root logger once with JSON format."""
    root = logging.getLogger()
    if getattr(root, '_annadan_logging_configured', False):
        return

    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())

    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    root._annadan_logging_configured = True
