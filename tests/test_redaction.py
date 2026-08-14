
from src.detectors.email import EmailDetector
from src.redaction import apply_redactions, resolve_non_overlapping
from src.replacement import ReplacementResolver


def test_replacement_is_deterministic():
    resolver = ReplacementResolver()

    first = resolver.replacement_for("PERSON", "Sarthak Malvadkar")
    second = resolver.replacement_for("PERSON", "Sarthak Malvadkar")

    assert first == second
    assert first != "Sarthak Malvadkar"


def test_replacement_is_scoped_by_entity_type():
    resolver = ReplacementResolver()

    person = resolver.replacement_for("PERSON", "same value")
    company = resolver.replacement_for("COMPANY", "same value")

    assert person != company


def test_apply_redactions_preserves_source_offsets():
    text = "Contact user@example.com and backup@example.com."
    detections = EmailDetector().detect(text, "TEST_001")

    redacted, audit = apply_redactions(
        text,
        detections,
        ReplacementResolver(),
    )

    assert redacted != text
    assert len(audit) == 2
    assert "user@example.com" not in redacted
    assert "backup@example.com" not in redacted


def test_overlapping_detections_keep_highest_confidence():
    detections = [
        {
            "entity_type": "PERSON",
            "text": "Jane Doe",
            "start": 0,
            "end": 8,
            "confidence": 0.80,
        },
        {
            "entity_type": "COMPANY",
            "text": "Jane",
            "start": 0,
            "end": 4,
            "confidence": 0.95,
        },
    ]

    accepted = resolve_non_overlapping(detections)

    assert [detection["text"] for detection in accepted] == ["Jane"]