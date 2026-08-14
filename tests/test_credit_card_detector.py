
from src.detectors.credit_card import CreditCardDetector


def test_valid_card():

    detector = CreditCardDetector()

    results = detector.detect(
        "Card: 4111111111111111",
        "TEST_001"
    )

    assert len(results) == 1
    assert results[0]["entity_type"] == "CREDIT_CARD"


def test_formatted_card():

    detector = CreditCardDetector()

    results = detector.detect(
        "Card: 4111 1111 1111 1111",
        "TEST_002"
    )

    assert len(results) == 1


def test_invalid_luhn():

    detector = CreditCardDetector()

    results = detector.detect(
        "Card: 4111111111111112",
        "TEST_003"
    )

    assert len(results) == 0


def test_financial_number_not_card():

    detector = CreditCardDetector()

    results = detector.detect(
        "Revenue: 56818200",
        "TEST_004"
    )

    assert len(results) == 0