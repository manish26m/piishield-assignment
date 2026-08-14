
from typing import Dict, Iterable, List, Tuple

from .address import AddressDetector
from .company import CompanyDetector
from .credit_card import CreditCardDetector
from .dob import DOBDetector
from .email import EmailDetector
from .ip import IPDetector
from .person import PersonDetector
from .phone import PhoneDetector
from .ssn import SSNDetector


class UnifiedDetector:
    """Run all configured PII detectors and return one ordered result set."""

    def __init__(self, detectors: Iterable = None):
        self.detectors = list(detectors) if detectors is not None else [
            EmailDetector(),
            PhoneDetector(),
            IPDetector(),
            CreditCardDetector(),
            SSNDetector(),
            PersonDetector(),
            CompanyDetector(),
            AddressDetector(),
            DOBDetector(),
        ]

    @staticmethod
    def _dedupe_key(detection: Dict) -> Tuple:
        return (
            detection.get("entity_type"),
            detection.get("start"),
            detection.get("end"),
            detection.get("text"),
        )

    def detect(self, text: str, element_id: str) -> List[Dict]:

        detections = []
        seen = set()

        for detector in self.detectors:
            for detection in detector.detect(text, element_id):
                detection.setdefault(
                    "detector",
                    getattr(detector, "detector_name", detector.__class__.__name__),
                )

                key = self._dedupe_key(detection)
                if key in seen:
                    continue

                seen.add(key)
                detections.append(detection)

        return sorted(
            detections,
            key=lambda detection: (
                detection.get("start", 0),
                detection.get("end", 0),
                detection.get("entity_type", ""),
            ),
        )