
from src.detectors.person import PersonDetector


def test_person_name():
    detector = PersonDetector()
    results = detector.detect(
        "Contact Person: John Smith",
        "TEST_001"
    )
    assert "John Smith" in [r["text"] for r in results]


def test_multiple_people():
    detector = PersonDetector()
    results = detector.detect(
        "John Smith and Mary Johnson attended the meeting.",
        "TEST_002"
    )
    names = [r["text"] for r in results]
    assert "John Smith" in names
    assert "Mary Johnson" in names


def test_no_person():
    detector = PersonDetector()
    results = detector.detect(
        "The company reported strong financial performance.",
        "TEST_003"
    )
    assert len(results) == 0


def test_generic_term_rejected():
    detector = PersonDetector()
    results = detector.detect(
        "The Offer and Promoters were discussed.",
        "TEST_004"
    )
    names = [r["text"].lower() for r in results]
    assert "offer" not in names
    assert "promoters" not in names


def test_email_context_rejected():
    detector = PersonDetector()
    results = detector.detect(
        "Email: John Smith Website: www.example.com",
        "TEST_005"
    )
    assert "John Smith" not in [r["text"] for r in results]


def test_contact_person_high_confidence():
    detector = PersonDetector()
    results = detector.detect(
        "Contact Person: Sarthak Malvadkar",
        "TEST_006"
    )

    matching = [
        r for r in results
        if r["text"] == "Sarthak Malvadkar"
    ]

    assert len(matching) == 1
    assert matching[0]["confidence"] >= 0.95


def test_slash_separated_people():
    detector = PersonDetector()
    results = detector.detect(
        "Contact Person: Kishan Rastogi/ Abhijit Diwan",
        "TEST_007"
    )

    names = [r["text"] for r in results]

    assert "Kishan Rastogi" in names
    assert "Abhijit Diwan" in names


def test_huf_suffix_removed():
    detector = PersonDetector()
    results = detector.detect(
        "Transfer to Karunakar Hegde HUF.",
        "TEST_008"
    )

    assert "Karunakar Hegde" in [
        r["text"] for r in results
    ]


def test_company_secretary_suffix_removed():
    detector = PersonDetector()
    results = detector.detect(
        "Sarthak Malvadkar Company Secretary and Compliance Officer",
        "TEST_009"
    )

    names = [r["text"] for r in results]

    assert "Sarthak Malvadkar" in names
    assert "Sarthak Malvadkar Company" not in names


def test_formatting_artifacts_removed():
    detector = PersonDetector()
    results = detector.detect(
        "Rajesh Kushal Hegde*^&",
        "TEST_010"
    )

    assert "Rajesh Kushal Hegde" in [
        r["text"] for r in results
    ]


def test_financial_category_rejected():
    detector = PersonDetector()

    for text in [
        "Mutual Funds",
        "UPI Bidders",
        "Key Managerial Personnel",
        "PAT CAGR",
        "B. Non-GAAP Measures",
        "Promoter Trusts",
    ]:
        results = detector.detect(
            text,
            "TEST_FINANCIAL"
        )

        assert len(results) == 0


def test_business_name_rejected():
    detector = PersonDetector()

    results = detector.detect(
        "Kushal Electricals",
        "TEST_BUSINESS"
    )

    assert len(results) == 0


def test_program_name_rejected():
    detector = PersonDetector()

    results = detector.detect(
        "Deen Dayal Upadhyaya Gram Jyoti",
        "TEST_PROGRAM"
    )

    assert len(results) == 0
from src.detectors.person import PersonDetector


def test_final_prospectus_false_positives_rejected():

    detector = PersonDetector()

    false_positives = [
        "C. Operational measures",
        "Bandra East, Mumbai – 400051",
        "through a Registered Broker",
        "Montreal Business Centre, Baner Pune",
        "DM Shetty and Gopal BO",
    ]

    for text in false_positives:

        results = detector.detect(
            text,
            "TEST_FINAL_FP"
        )

        assert len(results) == 0, (
            f"False positive detected in: {text}"
        )