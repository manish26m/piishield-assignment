
# PIIShield evaluation report

## Evaluation approach

The labeled regression set contains 12 cases covering all nine required PII categories, plus negative controls for ordinary dates, identifiers, and generic company references.

A prediction is a true positive when both `entity_type` and exact entity text match the labeled record. Accuracy is calculated over entity-level matches plus labeled negative cases. Precision, recall, and F1 are calculated per category and as an overall micro average.

## Results

| Category | Accuracy | Precision | Recall | F1 | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PERSON | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| EMAIL | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| PHONE | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| COMPANY | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| ADDRESS | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| SSN | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| CREDIT_CARD | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| DOB | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| IP_ADDRESS | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1 | 0 | 0 | 11 |
| OVERALL_MICRO | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 | 0 | 0 | 99 |

## Limitations

- This is a labeled regression set, not a complete manual annotation of all 4,288 prospectus elements.
- Prospectus-level recall requires a human-reviewed ground-truth file covering every expected PII span.
- The evaluation is reproducible and intended to catch detector regressions before submission.