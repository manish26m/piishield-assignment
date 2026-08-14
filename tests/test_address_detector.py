
from src.detectors.address import AddressDetector


def test_registered_office():
    detector = AddressDetector()

    results = detector.detect(
        "Registered Office: 11/3, 11/4 and 11/5, Village Birdewadi, Chakan Taluka - Khed, Pune – 410 501, Maharashtra, India",
        "TEST_001",
    )

    assert len(results) == 1
    assert results[0]["entity_type"] == "ADDRESS"
    assert "410 501" in results[0]["text"]


def test_corporate_office():
    detector = AddressDetector()

    results = detector.detect(
        "Corporate Office: 201, Tower 2, Montreal Business Centre, Off Pallod Farms, Baner, Pune – 411 045, Maharashtra, India",
        "TEST_002",
    )

    assert len(results) == 1
    assert "411 045" in results[0]["text"]


def test_address_without_office_label():
    detector = AddressDetector()

    results = detector.detect(
        "PCNTDA Green Building Block A 1st and 2nd floor Near Akurdi Railway Station Akurdi, Pune – 411 044 Maharashtra, India",
        "TEST_003",
    )

    assert len(results) == 1


def test_non_address_registration_number():
    detector = AddressDetector()

    results = detector.detect(
        "Registration number: 141032",
        "TEST_004",
    )

    assert len(results) == 0


def test_non_address_peer_review_number():
    detector = AddressDetector()

    results = detector.detect(
        "Peer review number: 014680",
        "TEST_005",
    )

    assert len(results) == 0


def test_normal_text_with_pune():
    detector = AddressDetector()

    results = detector.detect(
        "The registered office was shifted to Pune in 2011.",
        "TEST_006",
    )

    assert len(results) == 0


def test_address_with_phone():
    detector = AddressDetector()

    results = detector.detect(
        "ICICI Venture House, Appasaheb Marathe Marg, Prabhadevi, Mumbai – 400 025 Maharashtra, India Telephone: 022-68052182",
        "TEST_007",
    )

    assert len(results) == 1
    assert "400 025" in results[0]["text"]
    assert "Telephone" not in results[0]["text"]


def test_table_style_address():
    detector = AddressDetector()

    results = detector.detect(
        """Nuvama Wealth Management Limited
801 - 804, Wing A, Building No 3, Inspire BKC,
Bandra Kurla Complex, Bandra East, Mumbai 400051,
Maharashtra, India""",
        "TEST_008",
    )

    assert len(results) == 1
    assert "400051" in results[0]["text"]


def test_registration_number_with_address_words():
    detector = AddressDetector()

    results = detector.detect(
        "Registration number: 140388",
        "TEST_009",
    )

    assert len(results) == 0


def test_long_prospectus_paragraph_extracts_only_address():

    detector = AddressDetector()

    text = (
        "KSH International Limited, a public limited company "
        "having its Registered Office at 11/3, 11/4 and 11/5, "
        "Village Birdewadi, Chakan Taluka - Khed, Pune – 410 501, "
        "Maharashtra, India and its Corporate Office at 201, "
        "Tower 2, Montreal Business Centre, Off Pallod Farms, "
        "Baner, Pune – 411 045, Maharashtra, India."
    )

    results = detector.detect(
        text,
        "TEST_010",
    )

    assert len(results) == 2

    assert any(
        "410 501" in result["text"]
        for result in results
    )

    assert any(
        "411 045" in result["text"]
        for result in results
    )

    for result in results:
        assert "having its Registered Office" not in result["text"]
        assert "Corporate Office at" not in result["text"]


def test_address_stops_before_email():

    detector = AddressDetector()

    text = (
        "163, 5th Floor, H.T.Parekh Marg "
        "Backbay Reclamation Churchgate, Mumbai – 400020 "
        "Telephone: 022-68052182 "
        "Email: Ipocmg@icicibank.com "
        "Website: www.icicibank.com"
    )

    results = detector.detect(
        text,
        "TEST_011",
    )

    assert len(results) == 1

    result = results[0]["text"]

    assert "400020" in result
    assert "Telephone" not in result
    assert "Email" not in result
    assert "Website" not in result

def test_company_name_removed_from_address():
    detector = AddressDetector()

    text = (
        "ICICI Securities Limited ICICI Venture House Appasaheb Marathe Marg "
        "Prabhadevi, Mumbai – 400 025 Maharashtra, India"
    )

    results = detector.detect(
        text,
        "TEST_012",
    )

    assert len(results) == 1

    result = results[0]["text"]

    assert "ICICI Venture House" in result
    assert "ICICI Securities Limited" not in result
    assert "400 025" in result
    assert text[results[0]["start"]:results[0]["end"]] == result