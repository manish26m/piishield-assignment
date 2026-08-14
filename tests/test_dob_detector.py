
from src.detectors.dob import DOBDetector


def test_date_of_birth_with_numeric_date():
    detector = DOBDetector()

    text = "Date of Birth: 10/12/1999"
    results = detector.detect(text, "TEST_001")

    assert len(results) == 1
    assert results[0]["entity_type"] == "DOB"
    assert results[0]["text"] == "10/12/1999"
    assert text[results[0]["start"]:results[0]["end"]] == results[0]["text"]


def test_birth_date_with_textual_month():
    detector = DOBDetector()

    results = detector.detect(
        "Birth date - December 10, 1999",
        "TEST_002",
    )

    assert len(results) == 1
    assert results[0]["text"] == "December 10, 1999"


def test_born_on_with_iso_date():
    detector = DOBDetector()

    results = detector.detect(
        "The applicant was born on 1999-12-10.",
        "TEST_003",
    )

    assert len(results) == 1
    assert results[0]["text"] == "1999-12-10"


def test_dob_abbreviation():
    detector = DOBDetector()

    results = detector.detect(
        "DOB: 21 July 1985",
        "TEST_004",
    )

    assert len(results) == 1
    assert results[0]["text"] == "21 July 1985"


def test_date_without_dob_context_is_ignored():
    detector = DOBDetector()

    results = detector.detect(
        "The agreement was signed on December 10, 1999.",
        "TEST_005",
    )

    assert len(results) == 0


def test_invalid_calendar_date_is_ignored():
    detector = DOBDetector()

    results = detector.detect(
        "Date of Birth: 31/02/1999",
        "TEST_006",
    )

    assert len(results) == 0