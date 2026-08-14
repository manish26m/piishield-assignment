
import re
from typing import List, Dict

import phonenumbers

from .base import BaseDetector


class PhoneDetector(BaseDetector):

    entity_type = "PHONE"
    detector_name = "phone_regex_phonenumbers_context"

    PHONE_PATTERN = re.compile(
        r"(?<!\d)"
        r"(?:\+?\d[\d\s().-]{7,}\d)"
        r"(?!\d)"
    )

    # Strong indicators that a number is a phone number.
    PHONE_CONTEXT_PATTERN = re.compile(
        r"\b("
        r"telephone|tel|phone|mobile|mob|contact\s*(?:number|no)?"
        r"|call|fax"
        r")\b",
        re.IGNORECASE
    )

    # Strong indicators that a number is NOT a phone number.
    NON_PHONE_CONTEXT_PATTERN = re.compile(
        r"\b("
        r"reference\s*(?:number|no)?"
        r"|ref\.?\s*(?:number|no)?"
        r"|circular\s*(?:number|no)?"
        r"|registration\s*(?:number|no)?"
        r"|serial\s*(?:number|no)?"
        r"|folio\s*(?:number|no)?"
        r"|account\s*(?:number|no)?"
        r"|order\s*(?:number|no)?"
        r"|application\s*(?:number|no)?"
        r")\b",
        re.IGNORECASE
    )

    def detect(
        self,
        text: str,
        element_id: str
    ) -> List[Dict]:

        detections = []

        for match in self.PHONE_PATTERN.finditer(text):

            candidate = match.group().strip()

            candidate = candidate.rstrip(".,;:")

            digits = re.sub(r"\D", "", candidate)

            if len(digits) < 10:
                continue

            # --------------------------------------------------
            # Context around the candidate
            # --------------------------------------------------

            context_start = max(0, match.start() - 80)
            context_end = min(len(text), match.end() + 80)

            context = text[context_start:context_end]

            # --------------------------------------------------
            # Reject strong non-phone contexts
            # --------------------------------------------------

            if self.NON_PHONE_CONTEXT_PATTERN.search(context):
                continue

            # --------------------------------------------------
            # Validate using phonenumbers
            # --------------------------------------------------

            try:

                parsed = phonenumbers.parse(
                    candidate,
                    "IN"
                )

                if not phonenumbers.is_possible_number(parsed):
                    continue

                if not phonenumbers.is_valid_number(parsed):
                    continue

            except phonenumbers.NumberParseException:
                continue

            # --------------------------------------------------
            # Determine confidence
            # --------------------------------------------------

            confidence = 0.90

            if self.PHONE_CONTEXT_PATTERN.search(context):
                confidence = 0.99

            # Explicit international/Indian formatting is
            # additional evidence.
            if candidate.startswith("+91"):
                confidence = min(0.995, confidence + 0.005)

            detections.append({
                "element_id": element_id,
                "entity_type": self.entity_type,
                "text": candidate,
                "start": match.start(),
                "end": match.end(),
                "confidence": confidence,
                "detector": self.detector_name
            })

        return detections