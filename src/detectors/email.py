
import re
from typing import List, Dict

from .base import BaseDetector


class EmailDetector(BaseDetector):

    entity_type = "EMAIL"
    detector_name = "email_regex"

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )

    def detect(
        self,
        text: str,
        element_id: str
    ) -> List[Dict]:

        detections = []

        for match in self.EMAIL_PATTERN.finditer(text):

            detections.append({
                "element_id": element_id,
                "entity_type": self.entity_type,
                "text": match.group(),
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.99,
                "detector": self.detector_name
            })

        return detections