
import hashlib
import hmac
import ipaddress
import re
from typing import Optional


class PIISecurity:
    """Small local demonstrations of pseudonymization and masking controls."""

    def __init__(self, secret: str = "piishield-local-demo"):
        self.secret = secret.encode("utf-8")

    def hash_value(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def tokenize(self, value: str) -> str:
        digest = hmac.new(
            self.secret,
            value.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()[:16]
        return f"tok_{digest}"

    @staticmethod
    def mask_value(value: str, entity_type: str) -> str:
        if entity_type == "EMAIL" and "@" in value:
            local, domain = value.split("@", 1)
            visible = local[:1] if local else ""
            return f"{visible}***@{domain}"

        if entity_type == "PHONE":
            digits = re.sub(r"\D", "", value)
            return f"***{digits[-4:]}" if digits else "***"

        if entity_type == "CREDIT_CARD":
            digits = re.sub(r"\D", "", value)
            return f"**** **** **** {digits[-4:]}" if digits else "****"

        if entity_type == "SSN":
            digits = re.sub(r"\D", "", value)
            return f"***-**-{digits[-4:]}" if digits else "***-**-****"

        if len(value) <= 4:
            return "*" * len(value)

        return "*" * (len(value) - 4) + value[-4:]

    @staticmethod
    def generalize_ip(value: str) -> Optional[str]:
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            return None

        if address.version == 4:
            octets = value.split(".")
            return ".".join(octets[:2] + ["0", "0"]) + "/16"

        network = ipaddress.ip_network(f"{value}/64", strict=False)
        return str(network)