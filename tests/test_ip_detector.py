
from src.detectors.ip import IPDetector


def test_valid_ip():

    detector = IPDetector()

    results = detector.detect(
        "Server IP: 192.168.1.10",
        "TEST_001"
    )

    assert len(results) == 1
    assert results[0]["text"] == "192.168.1.10"


def test_multiple_ips():

    detector = IPDetector()

    results = detector.detect(
        "Servers: 10.0.0.1 and 8.8.8.8",
        "TEST_002"
    )

    assert len(results) == 2


def test_invalid_ip():

    detector = IPDetector()

    results = detector.detect(
        "Invalid: 999.999.999.999",
        "TEST_003"
    )

    assert len(results) == 0


def test_normal_number():

    detector = IPDetector()

    results = detector.detect(
        "Date: 2025.10.10",
        "TEST_004"
    )

    assert len(results) == 0