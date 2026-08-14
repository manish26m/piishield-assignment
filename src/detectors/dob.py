
import re
from datetime import datetime
from typing import Dict, List

from .base import BaseDetector


MONTH_PATTERN = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)


class DOBDetector(BaseDetector):

    entity_type = "DOB"
    detector_name = "dob_regex_context"

    DATE_PATTERN = re.compile(
        rf"(?<!\d)(?:"
        rf"(?:0?[1-9]|[12]\d|3[01])[./-](?:0?[1-9]|[12]\d|3[01])[./-]\d{{4}}"
        rf"|\d{{4}}[./-](?:0?[1-9]|1[0-2])[./-](?:0?[1-9]|[12]\d|3[01])"
        rf"|{MONTH_PATTERN}\s+(?:0?[1-9]|[12]\d|3[01])(?:st|nd|rd|th)?"
        rf"[,]?\s+\d{{4}}"
        rf"|(?:0?[1-9]|[12]\d|3[01])(?:st|nd|rd|th)?\s+"
        rf"{MONTH_PATTERN}\s+\d{{4}}"
        rf")(?!\d)",
        re.IGNORECASE,
    )

    DOB_CONTEXT = re.compile(
        r"\b(?:date\s+of\s+birth|birth\s+date|dob|born(?:\s+on)?)\b",
        re.IGNORECASE,
    )

    DATE_FORMATS = (
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%m.%d.%Y",
        "%Y/%m/%d",
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%B %d, %Y",
        "%B %d %Y",
        "%b %d, %Y",
        "%b %d %Y",
        "%d %B %Y",
        "%d %b %Y",
    )

    @classmethod
    def _is_valid_date(cls, candidate: str) -> bool:

        normalized = re.sub(
            r"(\d)(?:st|nd|rd|th)\b",
            r"\1",
            candidate,
            flags=re.IGNORECASE,
        )

        for date_format in cls.DATE_FORMATS:
            try:
                parsed = datetime.strptime(
                    normalized,
                    date_format,
                )
            except ValueError:
                continue

            return parsed.date() <= datetime.today().date()

        return False

    @classmethod
    def _has_dob_context(cls, text: str, start: int, end: int) -> bool:

        before = text[max(0, start - 80):start]
        after = text[end:min(len(text), end + 40)]

        return bool(
            cls.DOB_CONTEXT.search(before)
            or cls.DOB_CONTEXT.search(after)
        )

    def detect(
        self,
        text: str,
        element_id: str,
    ) -> List[Dict]:

        detections = []

        for match in self.DATE_PATTERN.finditer(text):

            candidate = match.group()

            if not self._is_valid_date(candidate):
                continue

            if not self._has_dob_context(
                text,
                match.start(),
                match.end(),
            ):
                continue

            detections.append({
                "element_id": element_id,
                "entity_type": self.entity_type,
                "text": candidate,
                "start": match.start(),
                "end": match.end(),
                "confidence": 0.98,
                "detector": self.detector_name,
            })

        return detections