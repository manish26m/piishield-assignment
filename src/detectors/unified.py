import re
from typing import Dict, Iterable, List, Tuple

import spacy

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

    NER_CONTEXT = re.compile(
        r"\b("
        r"contact\s+person|person\s*:|name\s+of|mr\.?|mrs\.?|ms\.?|"
        r"miss|shri|smt|director|promoter|company\s+secretary|"
        r"compliance\s+officer|managing\s+director|chief\s+executive\s+officer|"
        r"chief\s+financial\s+officer|key\s+managerial\s+personnel|"
        r"company|organization|organisation|brand|group|bank|securities|"
        r"industry|industries|technology|technologies|capital|ventures?|"
        r"holdings?|limited|ltd|private|llp|incorporated|corporation|corp"
        r")\b",
        re.IGNORECASE,
    )

    PERSON_NER_CONTEXT = re.compile(
        r"\b("
        r"contact\s+person|person\s*:|name\s+of|mr\.?|mrs\.?|ms\.?|"
        r"miss|shri|smt|director|promoter|company\s+secretary|"
        r"compliance\s+officer|managing\s+director|chief\s+executive\s+officer|"
        r"chief\s+financial\s+officer|key\s+managerial\s+personnel"
        r")\b",
        re.IGNORECASE,
    )

    COMPANY_NER_EVIDENCE = re.compile(
        r"\b("
        r"securities|bank|technology|technologies|capital|ventures?|holdings?|"
        r"private\s+limited|pvt\.?\s+(?:limited|ltd\.?)|limited|ltd\.?|"
        r"llp|incorporated|inc\.?|corporation|corp\.?"
        r")\b",
        re.IGNORECASE,
    )

    CAPITALIZED_SEQUENCE = re.compile(
        r"\b[A-Z][A-Za-z.&'-]*(?:\s+[A-Z][A-Za-z.&'-]*)+\b"
    )

    def __init__(self, detectors: Iterable = None):
        if detectors is not None:
            self.detectors = list(detectors)
            return

        shared_nlp = spacy.load("en_core_web_sm")
        self.detectors = [
            EmailDetector(),
            PhoneDetector(),
            IPDetector(),
            CreditCardDetector(),
            SSNDetector(),
            PersonDetector(nlp=shared_nlp),
            CompanyDetector(nlp=shared_nlp),
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

    def _detect(
        self,
        text: str,
        element_id: str,
        skip_detectors: Tuple[type, ...] = (),
    ) -> List[Dict]:

        detections = []
        seen = set()

        for detector in self.detectors:
            if skip_detectors and isinstance(detector, skip_detectors):
                continue

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

    def detect(self, text: str, element_id: str) -> List[Dict]:
        """Run every detector without changing the standard behavior."""

        return self._detect(text, element_id)

    def detect_many(
        self,
        items: Iterable[Tuple[str, str]],
        fast: bool = False,
    ) -> Dict[str, List[Dict]]:
        """Run a document batch while preserving per-element detections.

        spaCy's batch API avoids repeated pipeline setup for large DOCX files.
        The detector rules themselves are unchanged; this method only changes
        how the same text is scheduled for the two spaCy-backed detectors.
        """

        batch = list(items)
        grouped = {element_id: [] for _, element_id in batch}
        seen = {element_id: set() for _, element_id in batch}

        def add_detection(detection: Dict, detector) -> None:
            element_id = detection["element_id"]
            detection.setdefault(
                "detector",
                getattr(detector, "detector_name", detector.__class__.__name__),
            )
            key = self._dedupe_key(detection)
            if key in seen[element_id]:
                return
            seen[element_id].add(key)
            grouped[element_id].append(detection)

        for detector in self.detectors:
            if isinstance(detector, (PersonDetector, CompanyDetector)):
                detector_batch = batch
                if fast:
                    detector_batch = [
                        (text, element_id)
                        for text, element_id in batch
                        if self._should_run_ner(detector, text)
                    ]

                docs = detector.nlp.pipe(
                    (text for text, _ in detector_batch),
                    batch_size=64,
                )
                for (text, element_id), doc in zip(detector_batch, docs):
                    for detection in detector._detect_with_doc(
                        text,
                        element_id,
                        doc,
                    ):
                        add_detection(detection, detector)
                continue

            for text, element_id in batch:
                for detection in detector.detect(text, element_id):
                    add_detection(detection, detector)

        for element_id, detections in grouped.items():
            grouped[element_id] = sorted(
                detections,
                key=lambda detection: (
                    detection.get("start", 0),
                    detection.get("end", 0),
                    detection.get("entity_type", ""),
                ),
            )

        return grouped

    def _should_run_ner(self, detector, text: str) -> bool:
        if isinstance(detector, PersonDetector):
            return bool(
                self.PERSON_NER_CONTEXT.search(text)
                or (
                    len(text) <= 220
                    and self.CAPITALIZED_SEQUENCE.search(text)
                )
            )

        if isinstance(detector, CompanyDetector):
            return bool(
                self.COMPANY_NER_EVIDENCE.search(text)
                and (
                    self.CAPITALIZED_SEQUENCE.search(text)
                    or re.search(
                        r"\b(?:private\s+limited|pvt\.?\s+(?:limited|ltd\.?)|"
                        r"limited|ltd\.?|llp|incorporated|inc\.?|corporation|corp\.?)\b",
                        text,
                        re.IGNORECASE,
                    )
                )
            )

        return True

    def detect_many_fast(
        self,
        items: Iterable[Tuple[str, str]],
    ) -> Dict[str, List[Dict]]:
        """Batch the web upload path while gating only expensive NER scans."""

        return self.detect_many(items, fast=True)

    def detect_fast(self, text: str, element_id: str) -> List[Dict]:
        """Reduce unnecessary NER work for large interactive uploads."""

        skip_detectors = []

        if not self._should_run_ner(PersonDetector, text):
            skip_detectors.append(PersonDetector)

        if not self._should_run_ner(CompanyDetector, text):
            skip_detectors.append(CompanyDetector)

        return self._detect(text, element_id, tuple(skip_detectors))

