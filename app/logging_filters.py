import logging
import re


class SecretMaskingFilter(logging.Filter):
    PATTERNS = [
        re.compile(r"postgresql\+psycopg2://[^@]+@"),
        re.compile(r"password=[^&\s]+"),
        re.compile(r"(\btoken\b\s*=\s*)[A-Za-z0-9\.\-_]+", re.I),
    ]
    MASK = "*****"

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern in self.PATTERNS:
            msg = pattern.sub(self.MASK, msg)
        record.msg = msg
        return True
