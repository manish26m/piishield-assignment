
from src.detectors.email import EmailDetector
from src.detectors.ip import IPDetector
from src.detectors.unified import UnifiedDetector


def test_unified_detector_orders_and_deduplicates_results():
    detector = UnifiedDetector(
        detectors=[EmailDetector(), IPDetector()]
    )

    text = "Contact user@example.com from 192.168.1.10"
    results = detector.detect(text, "TEST_001")

    assert [result["entity_type"] for result in results] == [
        "EMAIL",
        "IP_ADDRESS",
    ]
    assert all(
        text[result["start"]:result["end"]] == result["text"]
        for result in results
    )


def test_unified_detector_preserves_detector_metadata():
    detector = UnifiedDetector(
        detectors=[EmailDetector()]
    )

    results = detector.detect("user@example.com", "TEST_002")

    assert len(results) == 1
    assert results[0]["detector"] == "email_regex"