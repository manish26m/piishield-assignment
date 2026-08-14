
import re
from typing import List, Dict

from .base import BaseDetector


class CreditCardDetector(BaseDetector):

    entity_type = "CREDIT_CARD"
    detector_name = "credit_card_regex_luhn"

    CARD_PATTERN = re.compile(
        r"(?<!\d)"
        r"(?:\d[ -]?){13,19}"
        r"(?!\d)"
    )

    @staticmethod
    def luhn_check(number: str) -> bool:
        """
        Validate a card number using the Luhn algorithm.
        """

        digits = [int(d) for d in number]

        checksum = 0
        parity = len(digits) % 2

        for index, digit in enumerate(digits):

            if index % 2 == parity:
                digit *= 2

                if digit > 9:
                    digit -= 9

            checksum += digit

        return checksum % 10 == 0

    def detect(
        self,
        text: str,
        element_id: str
    ) -> List[Dict]:

        detections = []

        for match in self.CARD_PATTERN.finditer(text):

            candidate = match.group()

            digits = re.sub(r"[\s-]", "", candidate)

            # Card numbers generally contain 13â€“19 digits.
            if not 13 <= len(digits) <= 19:
                continue

            if not self.luhn_check(digits):
                continue

            detections.append({
                "element_id": element_id,
                "entity_type": self.entity_type,
                "text": candidate,
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.99,
                "detector": self.detector_name
            })

        return detections