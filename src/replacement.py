
import hashlib
from typing import Dict


class ReplacementResolver:
    """Return deterministic synthetic replacements for detected entities."""

    def __init__(self):
        self._mapping: Dict[str, str] = {}

    @staticmethod
    def _code(entity_type: str, value: str) -> int:
        key = f"{entity_type}\0{value}".encode("utf-8")
        digest = hashlib.sha256(key).hexdigest()
        return 1000 + (int(digest[:8], 16) % 9000)

    def replacement_for(self, entity_type: str, value: str) -> str:
        key = f"{entity_type}\0{value}"

        if key in self._mapping:
            return self._mapping[key]

        code = self._code(entity_type, value)
        replacement = self._build_replacement(entity_type, code)
        self._mapping[key] = replacement

        return replacement

    @staticmethod
    def _build_replacement(entity_type: str, code: int) -> str:
        if entity_type == "PERSON":
            return f"Alex Morgan {code}"

        if entity_type == "EMAIL":
            return f"synthetic.{code}@example.test"

        if entity_type == "PHONE":
            return f"+91 90000 {code:04d}"

        if entity_type in {"IP", "IP_ADDRESS"}:
            return f"192.0.2.{1 + (code % 254)}"

        if entity_type == "CREDIT_CARD":
            return f"4000 0000 0000 {code:04d}"

        if entity_type == "SSN":
            return f"900-00-{code:04d}"

        if entity_type == "COMPANY":
            return f"Example Company {code} Limited"

        if entity_type == "ADDRESS":
            return f"Example Address {code}, Pune, Maharashtra, India"

        if entity_type == "DOB":
            return f"01/01/{1900 + (code % 100)}"

        return f"[REDACTED_{entity_type}_{code}]"