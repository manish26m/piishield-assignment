
from src.detectors.email import EmailDetector


def test_email_detection():

    detector = EmailDetector()

    text = "Contact us at test@example.com for more information."

    results = detector.detect(
        text=text,
        element_id="TEST_001"
    )

    assert len(results) == 1
    assert results[0]["entity_type"] == "EMAIL"
    assert results[0]["text"] == "test@example.com"


def test_multiple_emails():

    detector = EmailDetector()

    text = """
    Contact test@example.com or
    support@company.in for help.
    """

    results = detector.detect(
        text=text,
        element_id="TEST_002"
    )

    assert len(results) == 2