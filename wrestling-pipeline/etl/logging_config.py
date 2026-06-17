import logging
import json
import sys


class JsonFormatter(logging.Formatter):
    def format(self, record):
        payload = {
            "name": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record, self.datefmt),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(level=logging.INFO):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    if root.handlers:
        root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)


__all__ = ["configure_logging"]
