
import re

from src.detectors.base import BaseDetector


class AddressDetector(BaseDetector):

    ENTITY_TYPE = "ADDRESS"
    detector_name = "address_regex_context"

    PIN_PATTERN = re.compile(
        r"\b\d{3}\s?\d{3}\b"
    )

    ADDRESS_CONTEXT = re.compile(
        r"""
        \b(
            registered\s+office|
            corporate\s+office|
            branch\s+office|
            office|
            address|
            located\s+at|
            situated\s+at|
            plot\s*(?:no\.?|number)?|
            flat\s*(?:no\.?|number)?|
            floor|
            road|
            marg|
            lane|
            street|
            building|
            complex|
            industrial\s+area|
            industrial\s+park|
            village|
            taluka|
            district|
            nagar|
            residency|
            apartment|
            bunglow|
            society|
            railway\s+station|
            mumbai|
            pune|
            maharashtra|
            india
        )\b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    NON_ADDRESS_CONTEXT = re.compile(
        r"""
        \b(
            registration\s+number|
            registration\s+no|
            firm\s+registration|
            peer\s+review\s+number|
            peer\s+review\s+no|
            certificate\s+number|
            reference\s+number|
            circular\s+number|
            sebi\s+registration\s+number|
            telephone|
            phone|
            mobile|
            account\s+number|
            client\s+id|
            dp\s+id
        )\b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    # Strong phrases that indicate where an address begins.
    ADDRESS_START = re.compile(
        r"""
        (
            registered\s+office\s*:\s*|
            corporate\s+office\s*:\s*|
            branch\s+office\s*:\s*|
            registered\s+office\s+at\s+|
            corporate\s+office\s+at\s+|
            office\s+at\s+|
            located\s+at\s+|
            situated\s+at\s+|
            plant\s+at\s+|
            plant\s+located\s+at\s+|
            manufacturing\s+facility\s+located\s+at\s+|
            having\s+its\s+registered\s+office\s+at\s+|
            having\s+its\s+corporate\s+office\s+at\s+|
            plot\s+no\.?\s*|
            flat\s+no\.?\s*
        )
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    TRAILING_METADATA = re.compile(
        r"""
        \s+
        (?:
            telephone|
            tel\.?|
            phone|
            mobile|
            e[-\s]?mail|
            email|
            website|
            contact\s+person|
            sebi\s+registration\s+number|
            firm\s+registration\s+number|
            peer\s+review\s+number
        )
        \s*:
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    def _remove_leading_company_name(self, candidate):
        company_patterns = [
            r"^ICICI Securities Limited\s+",
            r"^Nuvama Wealth Management Limited\s+",
            r"^MUFG Intime India Private Limited\s+",
            r"^Hingne Tare & Associates\s+",
        ]

        for pattern in company_patterns:
            candidate = re.sub(
                pattern,
                "",
                candidate,
                flags=re.IGNORECASE,
            )

        return candidate.strip()

    def _extract_candidate(self, text, pin_match):

        pin_end = pin_match.end()

        # Address always ends at the PIN.
        end = pin_end

        # Search backwards for a strong address-start phrase.
        window_start = max(0, pin_match.start() - 600)
        before = text[window_start:pin_match.start()]

        starts = list(self.ADDRESS_START.finditer(before))

        if starts:
            start = window_start + starts[-1].end()
        else:
            # Fall back to the current line.
            line_start = text.rfind("\n", 0, pin_match.start())

            if line_start == -1:
                start = window_start
            else:
                start = line_start + 1

        candidate = text[start:end].strip()

        # Remove leading punctuation.
        candidate = candidate.lstrip(" :,-;")

        # If the extracted text is still clearly prose, trim
        # common introductory wording.
        prefixes = [
            "the company",
            "our company",
            "the corporate office of our company",
            "the registered office of our company",
            "our manufacturing facility",
        ]

        lowered = candidate.lower()

        for prefix in prefixes:
            if lowered.startswith(prefix):
                candidate = candidate[len(prefix):].lstrip(
                    " ,:-"
                )
                lowered = candidate.lower()
                candidate = self._remove_leading_company_name(candidate)

        # A company name may lead the address even when no prose prefix
        # was removed above.
        candidate = self._remove_leading_company_name(candidate)

        # Recalculate offsets from the exact cleaned substring.
        if candidate:
            candidate_offset = text.find(candidate, start, end)

            if candidate_offset != -1:
                start = candidate_offset
                end = candidate_offset + len(candidate)

        return candidate, start, end

    def detect(self, text: str, element_id: str):

        if not text:
            return []

        results = []

        for match in self.PIN_PATTERN.finditer(text):

            # Reject PIN-like values associated with obvious
            # non-address identifiers.
            before_pin = text[
                max(0, match.start() - 100):
                match.start()
            ]

            if self.NON_ADDRESS_CONTEXT.search(before_pin):
                continue

            # Require address-like context around the PIN.
            context = text[
                max(0, match.start() - 250):
                min(len(text), match.end() + 100)
            ]

            if not self.ADDRESS_CONTEXT.search(context):
                continue

            candidate, start, end = self._extract_candidate(
                text,
                match
            )

            if len(candidate) < 15:
                continue

            results.append(
                {
                    "element_id": element_id,
                    "entity_type": self.ENTITY_TYPE,
                    "text": candidate,
                    "start": start,
                    "end": end,
                    "confidence": 0.95,
                }
            )

        return results