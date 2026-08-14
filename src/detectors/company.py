
import re
from typing import Dict, List, Set, Tuple

import spacy

from .base import BaseDetector


class CompanyDetector(BaseDetector):

    entity_type = "COMPANY"
    detector_name = "spacy_org_legal_suffix_rules"

    LEGAL_NAME_PATTERN = re.compile(
        r"(?<![\w])"
        r"(?:[A-Z][A-Za-z0-9&.'-]*\s+){0,8}"
        r"(?:private\s+limited|pvt\.?\s+(?:limited|ltd\.?)|"
        r"limited|ltd\.?|llp|incorporated|inc\.?|corporation|corp\.?)"
        r"(?=$|[^\w])",
        re.IGNORECASE,
    )

    COMPANY_CONTEXT = re.compile(
        r"\b(?:company|organization|organisation|bank|securities|"
        r"industr(?:y|ies)|technology|technologies|capital|ventures?|"
        r"holdings?|limited|ltd|private|llp|incorporated|corporation|"
        r"corp)\b",
        re.IGNORECASE,
    )

    EXPLICIT_COMPANY_CONTEXT = re.compile(
        r"\b(?:company|organization|organisation|brand|group)\b",
        re.IGNORECASE,
    )

    GENERIC_NAMES = {
        "company",
        "the company",
        "our company",
        "organization",
        "organisation",
        "the organization",
        "the organisation",
    }

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    @staticmethod
    def _clean_candidate(candidate: str) -> str:
        return candidate.strip(" ,.;:()[]{}")

    @classmethod
    def _is_generic_name(cls, candidate: str) -> bool:
        normalized = re.sub(r"\s+", " ", candidate.lower()).strip()
        return normalized in cls.GENERIC_NAMES

    @classmethod
    def _has_company_evidence(
        cls,
        candidate: str,
        text: str,
        start: int,
        end: int,
    ) -> bool:
        if cls.LEGAL_NAME_PATTERN.fullmatch(candidate):
            return True

        if cls.COMPANY_CONTEXT.search(candidate):
            return True

        context = text[max(0, start - 60):min(len(text), end + 60)]
        return bool(cls.EXPLICIT_COMPANY_CONTEXT.search(context))

    @staticmethod
    def _key(start: int, end: int, candidate: str) -> Tuple[int, int, str]:
        return start, end, candidate.lower()

    def _make_detection(
        self,
        text: str,
        candidate: str,
        start: int,
        end: int,
        confidence: float,
    ) -> Dict:
        return {
            "element_id": "",
            "entity_type": self.entity_type,
            "text": candidate,
            "start": start,
            "end": end,
            "confidence": confidence,
            "detector": self.detector_name,
        }

    def detect(
        self,
        text: str,
        element_id: str,
    ) -> List[Dict]:

        detections = []
        seen: Set[Tuple[int, int, str]] = set()

        def add_candidate(
            candidate: str,
            start: int,
            end: int,
            confidence: float,
        ) -> None:
            candidate = self._clean_candidate(candidate)

            if not candidate or self._is_generic_name(candidate):
                return

            exact_start = text.find(candidate, start, end)
            if exact_start == -1:
                return

            exact_end = exact_start + len(candidate)
            key = self._key(exact_start, exact_end, candidate)

            if key in seen:
                return

            if not self._has_company_evidence(
                candidate,
                text,
                exact_start,
                exact_end,
            ):
                return

            seen.add(key)
            detection = self._make_detection(
                text,
                candidate,
                exact_start,
                exact_end,
                confidence,
            )
            detection["element_id"] = element_id
            detections.append(detection)

        for match in self.LEGAL_NAME_PATTERN.finditer(text):
            add_candidate(
                match.group(),
                match.start(),
                match.end(),
                0.97,
            )

        doc = self.nlp(text)

        for entity in doc.ents:
            if entity.label_ != "ORG":
                continue

            add_candidate(
                entity.text,
                entity.start_char,
                entity.end_char,
                0.90,
            )

        return sorted(
            detections,
            key=lambda detection: (
                detection["start"],
                detection["end"],
            ),
        )