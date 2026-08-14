
import re
from typing import List, Dict

from .base import BaseDetector


class SSNDetector(BaseDetector):

    entity_type = "SSN"
    detector_name = "ssn_regex_context"

    SSN_PATTERN = re.compile(
        r"(?<!\d)"
        r"(?:\d{3}[- ]?\d{2}[- ]?\d{4})"
        r"(?!\d)"
    )

    SSN_CONTEXT_PATTERN = re.compile(
        r"\b("
        r"ssn"
        r"|social\s+security"
        r"|social\s+security\s+number"
        r")\b",
        re.IGNORECASE
    )

    NON_SSN_CONTEXT_PATTERN = re.compile(
        r"\b("
        r"reference\s+(?:number|no)"
        r"|ref\.?\s*(?:number|no)"
        r"|registration\s+(?:number|no)"
        r"|serial\s+(?:number|no)"
        r"|folio\s+(?:number|no)"
        r"|account\s+(?:number|no)"
        r"|application\s+(?:number|no)"
        r"|circular\s+(?:number|no)"
        r"|firm\s+registration"
        r"|certificate\s+(?:number|no)"
        r")\b",
        re.IGNORECASE
    )

    def detect(
        self,
        text: str,
        element_id: str
    ) -> List[Dict]:

        detections = []

        for match in self.SSN_PATTERN.finditer(text):

            candidate = match.group()

            digits = re.sub(r"[- ]", "", candidate)

            if len(digits) != 9:
                continue

            area = digits[:3]
            group = digits[3:5]
            serial = digits[5:]

            if area == "000":
                continue

            if group == "00":
                continue

            if serial == "0000":
                continue

            # Look around the candidate.
            context_start = max(0, match.start() - 80)
            context_end = min(len(text), match.end() + 80)

            context = text[context_start:context_end]

            # Explicit negative context.
            if self.NON_SSN_CONTEXT_PATTERN.search(context):
                continue

            # Require explicit SSN context.
            if not self.SSN_CONTEXT_PATTERN.search(context):
                continue

            confidence = 0.99

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