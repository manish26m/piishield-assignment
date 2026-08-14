
from src.detectors.phone import PhoneDetector


def test_indian_phone():

    detector = PhoneDetector()

    text = "Call us at +91 20 45053237."

    results = detector.detect(
        text=text,
        element_id="TEST_001"
    )

    assert len(results) == 1
    assert results[0]["entity_type"] == "PHONE"


def test_phone_with_hyphens():

    detector = PhoneDetector()

    text = "Telephone: +91-20-45053237"

    results = detector.detect(
        text=text,
        element_id="TEST_002"
    )

    assert len(results) == 1


def test_normal_number_not_phone():

    detector = PhoneDetector()

    text = "The company issued 56,818,200 shares."

    results = detector.detect(
        text=text,
        element_id="TEST_003"
    )

    assert len(results) == 0


def test_reference_number_not_phone():

    detector = PhoneDetector()

    text = (
        "BSE having reference number "
        "20220803-40 dated August 3, 2022."
    )

    results = detector.detect(
        text=text,
        element_id="TEST_004"
    )

    assert len(results) == 0


def test_explicit_phone_context():

    detector = PhoneDetector()

    text = (
        "Contact Person: John Doe; "
        "Telephone: +91 20 45053237"
    )

    results = detector.detect(
        text=text,
        element_id="TEST_005"
    )

    assert len(results) == 1
    assert results[0]["confidence"] >= 0.99