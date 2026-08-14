
from src.detectors.ssn import SSNDetector


def test_valid_ssn():

    detector = SSNDetector()

    results = detector.detect(
        "SSN: 123-45-6789",
        "TEST_001"
    )

    assert len(results) == 1
    assert results[0]["entity_type"] == "SSN"


def test_ssn_without_hyphens():

    detector = SSNDetector()

    results = detector.detect(
        "Social Security Number: 123456789",
        "TEST_002"
    )

    assert len(results) == 1


def test_invalid_area():

    detector = SSNDetector()

    results = detector.detect(
        "SSN: 000-45-6789",
        "TEST_003"
    )

    assert len(results) == 0


def test_invalid_group():

    detector = SSNDetector()

    results = detector.detect(
        "SSN: 123-00-6789",
        "TEST_004"
    )

    assert len(results) == 0


def test_invalid_serial():

    detector = SSNDetector()

    results = detector.detect(
        "SSN: 123-45-0000",
        "TEST_005"
    )

    assert len(results) == 0


def test_reference_number_not_ssn():

    detector = SSNDetector()

    results = detector.detect(
        "Reference number: 123456789",
        "TEST_006"
    )

    assert len(results) == 0


def test_random_nine_digits_not_ssn():

    detector = SSNDetector()

    results = detector.detect(
        "Value: 123456789",
        "TEST_007"
    )

    assert len(results) == 0