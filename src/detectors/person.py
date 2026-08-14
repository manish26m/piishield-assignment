
import re
from typing import List, Dict

import spacy

from .base import BaseDetector


class PersonDetector(BaseDetector):

    entity_type = "PERSON"
    detector_name = "spacy_person_context_v4"

    POSITIVE_CONTEXT = re.compile(
        r"\b("
        r"contact\s+person"
        r"|person\s*:"
        r"|name\s+of"
        r"|mr\.?"
        r"|mrs\.?"
        r"|ms\.?"
        r"|miss"
        r"|shri"
        r"|smt"
        r"|director"
        r"|promoter"
        r"|company\s+secretary"
        r"|compliance\s+officer"
        r"|managing\s+director"
        r"|chief\s+executive\s+officer"
        r"|chief\s+financial\s+officer"
        r"|key\s+managerial\s+personnel"
        r")\b",
        re.IGNORECASE
    )

    NON_PERSON_CONTEXT = re.compile(
        r"\b("
        r"website"
        r"|email"
        r"|e-mail"
        r"|telephone"
        r"|tel"
        r"|address"
        r"|floor\s+price"
        r"|cap\s+price"
        r"|offer\s+price"
        r"|bid\s+amount"
        r"|reference\s+number"
        r"|registration\s+number"
        r"|circular"
        r"|private\s+limited"
        r"|limited"
        r"|llp"
        r"|hospital"
        r"|road"
        r"|marg"
        r"|complex"
        r"|taluka"
        r"|village"
        r"|branch"
        r"|facility"
        r"|newspaper"
        r"|transfer\s+agents"
        r"|acknowledgement\s+slip"
        r"|schedule"
        r")\b",
        re.IGNORECASE
    )

    DOMAIN_EXCLUSIONS = {
        # Financial / investment terminology
        "mutual funds",
        "mutual fund",
        "upi bidders",
        "individual bidders",
        "bidders",
        "bidder",
        "depository participant",
        "promoter trusts",
        "promoter trust",
        "key managerial personnel",
        "key managerial",
        "selling shareholder",
        "share transfer agents",
        "secondary transfer of",
        "wilful defaulter",

        # Financial metrics / headings
        "pat cagr",
        "pat margin",
        "b non-gaap",
        "c operational",
        "reference rate",

        # Business / organization references
        "kushal electricals",
        "supa facility",

        # Programs / schemes
        "gram jyoti",
        "kisan urja suraksha",

        # Generic descriptive phrases
        "air conditioning",
        "mega volt-amperes",
        "gigawatt-hour",
        "photo voltaic",
        "circuit kilometers",
        "acknowledgement slip",
        "registered broker",
        "bidder's dp id",
        "nro account",
        "tanishq showroom",
        "listing sebi bhavan",
        "buena monte",

        # Final prospectus-specific false positives
        "c. operational",
        "bandra east",
        "a registered broker",
        "baner pune",
        "gopal bo",
    }

    TRAILING_NON_NAME = re.compile(
        r"\s+(?:"
        r"company"
        r"|company\s+secretary"
        r"|compliance\s+officer"
        r"|huf"
        r"|website"
        r"|email"
        r"|e-mail"
        r"|director"
        r"|promoter"
        r")\s*$",
        re.IGNORECASE
    )

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def _clean_candidate(self, candidate: str) -> str:

        candidate = candidate.strip()

        # Remove formatting artifacts.
        candidate = re.sub(r"[*^&]+$", "", candidate).strip()

        # Remove leading/trailing punctuation.
        candidate = candidate.strip(" ,.;:()[]{}")

        # Remove trailing legal / role suffixes.
        previous = None

        while previous != candidate:
            previous = candidate
            candidate = self.TRAILING_NON_NAME.sub(
                "",
                candidate
            ).strip()

        return candidate

    def _is_domain_excluded(self, candidate: str) -> bool:

        normalized = re.sub(
            r"\s+",
            " ",
            candidate.lower()
        ).strip()

        if normalized in self.DOMAIN_EXCLUSIONS:
            return True

        # Reject candidates containing strong financial/legal terminology.
        forbidden_terms = (
            "cagr",
            "non-gaap",
            "bidder",
            "bidders",
            "mutual fund",
            "depository participant",
            "share transfer",
            "promoter trust",
            "air conditioning",
            "megawatt",
            "gigawatt",
            "photovoltaic",
            "circuit kilometer",
        )

        return any(
            term in normalized
            for term in forbidden_terms
        )

    def _looks_like_person_name(self, candidate: str) -> bool:

        words = candidate.split()

        if len(words) < 2:
            return False

        if len(words) > 4:
            return False

        # Every token in a conventional name should be alphabetic,
        # allowing initials such as "N.".
        for word in words:

            cleaned = word.rstrip(".")

            if not cleaned.isalpha():
                return False

        candidate_doc = self.nlp(candidate)

        tokens = [
            token
            for token in candidate_doc
            if not token.is_punct
        ]

        if len(tokens) < 2:
            return False

        proper_count = sum(
            token.pos_ == "PROPN"
            for token in tokens
        )

        # Require at least two proper-name tokens.
        if proper_count < 2:
            return False

        return True

    def detect(
        self,
        text: str,
        element_id: str
    ) -> List[Dict]:

        detections = []

        doc = self.nlp(text)

        for entity in doc.ents:

            if entity.label_ != "PERSON":
                continue

            raw_candidate = entity.text.strip()

            if not raw_candidate:
                continue

            # Split multiple people joined by slash.
            parts = re.split(
                r"\s*/\s*",
                raw_candidate
            )

            search_start = entity.start_char

            for part in parts:

                candidate = self._clean_candidate(part)

                if not candidate:
                    continue

                if self._is_domain_excluded(candidate):
                    continue

                if any(
                    char.isdigit()
                    for char in candidate
                ):
                    continue

                if not self._looks_like_person_name(candidate):
                    continue

                relative_start = raw_candidate.find(part)

                if relative_start < 0:
                    relative_start = 0

                start = search_start + relative_start
                end = start + len(candidate)

                context_start = max(
                    0,
                    start - 100
                )

                context_end = min(
                    len(text),
                    end + 100
                )

                context = text[
                    context_start:context_end
                ]

                # Strong negative context.
                if self.NON_PERSON_CONTEXT.search(context):

                    # Allow a strong person-specific context
                    # to override surrounding role words.
                    if not self.POSITIVE_CONTEXT.search(context):
                        continue

                confidence = 0.82

                if self.POSITIVE_CONTEXT.search(context):
                    confidence = 0.96

                detections.append({
                    "element_id": element_id,
                    "entity_type": self.entity_type,
                    "text": candidate,
                    "start": start,
                    "end": end,
                    "confidence": confidence,
                    "detector": self.detector_name
                })

        return detections