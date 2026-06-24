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

        # Include any extra fields passed via `extra` in logging calls
        skip_keys = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'exc_info',
            'exc_text', 'stack_info', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
            'thread', 'threadName', 'processName', 'process'
        }
        for k, v in record.__dict__.items():
            if k in skip_keys:
                continue
            if k in payload:
                continue
            try:
                json.dumps(v)
                payload[k] = v
            except Exception:
                payload[k] = str(v)

        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level=logging.INFO):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    if root.handlers:
        root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)


__all__ = ["configure_logging"]
