
import re
import ipaddress
from typing import List, Dict

from .base import BaseDetector


class IPDetector(BaseDetector):

    entity_type = "IP_ADDRESS"
    detector_name = "ipv4_regex_validation"

    IP_PATTERN = re.compile(
        r"(?<![\d.])"
        r"(?:\d{1,3}\.){3}\d{1,3}"
        r"(?![\d.])"
    )

    def detect(
        self,
        text: str,
        element_id: str
    ) -> List[Dict]:

        detections = []

        for match in self.IP_PATTERN.finditer(text):

            candidate = match.group()

            try:
                ipaddress.ip_address(candidate)

            except ValueError:
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