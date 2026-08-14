
from src.evaluate import evaluate_cases


class FakeDetector:
    def detect(self, text, element_id):
        if text == "positive":
            return [{
                "entity_type": "EMAIL",
                "text": "x@example.com",
            }]
        return []


def test_evaluation_reports_per_category_metrics():
    cases = [
        {
            "id": "positive",
            "text": "positive",
            "expected": [{
                "entity_type": "EMAIL",
                "text": "x@example.com",
            }],
        },
        {
            "id": "negative",
            "text": "negative",
            "expected": [],
        },
    ]

    metrics = evaluate_cases(cases, FakeDetector())

    assert metrics["EMAIL"]["tp"] == 1
    assert metrics["EMAIL"]["fp"] == 0
    assert metrics["EMAIL"]["fn"] == 0
    assert metrics["EMAIL"]["precision"] == 1.0
    assert metrics["EMAIL"]["recall"] == 1.0