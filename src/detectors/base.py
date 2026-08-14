
from abc import ABC, abstractmethod
from typing import List, Dict


class BaseDetector(ABC):
    """
    Base interface for all PII detectors.

    Every detector receives one normalized text string
    and returns a list of detected entities.
    """

    entity_type = "UNKNOWN"
    detector_name = "base"

    @abstractmethod
    def detect(
        self,
        text: str,
        element_id: str
    ) -> List[Dict]:
        """
        Detect PII entities in the supplied text.
        """
        pass