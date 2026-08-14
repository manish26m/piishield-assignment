
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.detectors.unified import UnifiedDetector


CATEGORIES = (
    "PERSON",
    "EMAIL",
    "PHONE",
    "COMPANY",
    "ADDRESS",
    "SSN",
    "CREDIT_CARD",
    "DOB",
    "IP_ADDRESS",
)


def _entity_set(records: Iterable[Dict], entity_type: str) -> Set[str]:
    return {
        record["text"]
        for record in records
        if record.get("entity_type") == entity_type
    }


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def evaluate_cases(
    cases: List[Dict],
    detector,
) -> Dict:
    metrics = {}

    for category in CATEGORIES:
        tp = fp = fn = tn = 0

        for case in cases:
            expected = _entity_set(case.get("expected", []), category)
            predicted = _entity_set(
                detector.detect(case["text"], case["id"]),
                category,
            )

            tp += len(expected & predicted)
            fp += len(predicted - expected)
            fn += len(expected - predicted)

            if not expected and not predicted:
                tn += 1

        precision = _safe_divide(tp, tp + fp)
        recall = _safe_divide(tp, tp + fn)
        f1 = _safe_divide(
            2 * precision * recall,
            precision + recall,
        )
        accuracy = _safe_divide(
            tp + tn,
            tp + tn + fp + fn,
        )

        metrics[category] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "tn": tn,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }

    totals = {
        field: sum(metrics[category][field] for category in CATEGORIES)
        for field in ("tp", "fp", "fn", "tn")
    }
    micro_precision = _safe_divide(
        totals["tp"],
        totals["tp"] + totals["fp"],
    )
    micro_recall = _safe_divide(
        totals["tp"],
        totals["tp"] + totals["fn"],
    )

    metrics["OVERALL_MICRO"] = {
        **totals,
        "accuracy": round(
            _safe_divide(
                totals["tp"] + totals["tn"],
                sum(totals.values()),
            ),
            4,
        ),
        "precision": round(micro_precision, 4),
        "recall": round(micro_recall, 4),
        "f1": round(
            _safe_divide(
                2 * micro_precision * micro_recall,
                micro_precision + micro_recall,
            ),
            4,
        ),
    }

    return metrics


def render_report(cases: List[Dict], metrics: Dict) -> str:
    lines = [
        "# PIIShield evaluation report",
        "",
        "## Evaluation approach",
        "",
        f"The labeled regression set contains {len(cases)} cases covering all nine required PII categories, plus negative controls for ordinary dates, identifiers, and generic company references.",
        "",
        "A prediction is a true positive when both `entity_type` and exact entity text match the labeled record. Accuracy is calculated over entity-level matches plus labeled negative cases. Precision, recall, and F1 are calculated per category and as an overall micro average.",
        "",
        "## Results",
        "",
        "| Category | Accuracy | Precision | Recall | F1 | TP | FP | FN | TN |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for category in CATEGORIES + ("OVERALL_MICRO",):
        row = metrics[category]
        lines.append(
            f"| {category} | {row['accuracy']:.4f} | {row['precision']:.4f} | {row['recall']:.4f} | {row['f1']:.4f} | {row['tp']} | {row['fp']} | {row['fn']} | {row['tn']} |"
        )

    lines.extend([
        "",
        "## Limitations",
        "",
        "- This is a labeled regression set, not a complete manual annotation of all 4,288 prospectus elements.",
        "- Prospectus-level recall requires a human-reviewed ground-truth file covering every expected PII span.",
        "- The evaluation is reproducible and intended to catch detector regressions before submission.",
    ])

    return "\n".join(lines) + "\n"


def main():
    ground_truth_path = PROJECT_ROOT / "evaluation" / "ground_truth.json"
    report_path = PROJECT_ROOT / "evaluation" / "evaluation_report.md"
    metrics_path = PROJECT_ROOT / "evaluation" / "evaluation_metrics.json"

    payload = json.loads(ground_truth_path.read_text(encoding="utf-8"))
    cases = payload["cases"]
    metrics = evaluate_cases(cases, UnifiedDetector())

    report_path.write_text(
        render_report(cases, metrics),
        encoding="utf-8",
    )
    metrics_path.write_text(
        json.dumps(
            {
                "ground_truth_cases": len(cases),
                "metrics": metrics,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    gold_metrics_path = PROJECT_ROOT / "data" / "gold" / "evaluation_metrics.json"
    gold_payload = {}
    if gold_metrics_path.exists():
        gold_payload = json.loads(
            gold_metrics_path.read_text(encoding="utf-8")
        )
    gold_payload.update({
        "evaluation_status": "evaluated",
        "reason": "Labeled regression metrics generated by src/evaluate.py.",
        "ground_truth_cases": len(cases),
        "metrics": metrics,
    })
    gold_metrics_path.write_text(
        json.dumps(gold_payload, indent=2),
        encoding="utf-8",
    )

    print(f"Evaluation cases : {len(cases)}")
    print(f"Report           : {report_path}")
    print(f"Metrics          : {metrics_path}")
    for category in CATEGORIES + ("OVERALL_MICRO",):
        row = metrics[category]
        print(
            f"{category:<14} accuracy={row['accuracy']:.4f} "
            f"precision={row['precision']:.4f} "
            f"recall={row['recall']:.4f} f1={row['f1']:.4f}"
        )


if __name__ == "__main__":
    main()