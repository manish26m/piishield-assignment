
from src.detectors.company import CompanyDetector


def test_legal_company_name():
    detector = CompanyDetector()

    text = "ICICI Securities Limited appointed a contact person."
    results = detector.detect(text, "TEST_001")

    assert len(results) == 1
    assert results[0]["text"] == "ICICI Securities Limited"
    assert text[results[0]["start"]:results[0]["end"]] == results[0]["text"]


def test_ner_company_name():
    detector = CompanyDetector()

    results = detector.detect(
        "Nuvama Wealth Management Limited is the registrar.",
        "TEST_002",
    )

    assert len(results) == 1
    assert results[0]["text"] == "Nuvama Wealth Management Limited"


def test_person_mislabeled_as_org_is_not_returned_without_company_evidence():
    detector = CompanyDetector()

    results = detector.detect(
        "HDFC Bank Limited appointed Varun Badai.",
        "TEST_003",
    )

    assert [result["text"] for result in results] == ["HDFC Bank Limited"]


def test_generic_company_reference_is_ignored():
    detector = CompanyDetector()

    results = detector.detect(
        "The Company announced its annual results.",
        "TEST_004",
    )

    assert len(results) == 0