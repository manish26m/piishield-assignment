
# PIIShield architecture

## End-to-end architecture

```mermaid
flowchart TD
    A[Source DOCX] --> B[DOCX ingestion]
    B --> C[Bronze JSONL]
    C --> D[Unicode and whitespace normalization]
    D --> E[Silver Parquet]
    E --> F[UnifiedDetector]
    F --> G[Regex detectors]
    F --> H[Validated numeric detectors]
    F --> I[spaCy NER detectors]
    F --> J[Context-aware detectors]
    G --> K[Entity records]
    H --> K
    I --> K
    J --> K
    K --> L[Deduplication and ordering]
    L --> M[Detection output]
```

## Layer responsibilities

| Layer | Input | Output | Responsibility |
|---|---|---|---|
| Bronze | DOCX | JSONL | Preserve extracted paragraphs and table cells |
| Silver | Bronze JSONL | Parquet | Normalize text without losing the original |
| Detection | Silver Parquet | Entity records | Identify PII with offsets and confidence |
| Unified | Detector results | Ordered result set | Run all detectors and remove exact duplicates |

## Detection flow

```mermaid
sequenceDiagram
    participant S as Silver element
    participant U as UnifiedDetector
    participant D as Category detector
    participant V as Validator or context rules
    participant O as Entity output

    S->>U: normalized_text + element_id
    U->>D: detect(text, element_id)
    D->>V: validate candidate
    V-->>D: accept or reject
    D-->>U: structured detections
    U->>U: deduplicate and sort by offset
    U-->>O: ordered entity records
```

## Detection record contract

Every detector returns a list of dictionaries with this shape:

```json
{
  "element_id": "P_00123",
  "entity_type": "EMAIL",
  "text": "someone@example.com",
  "start": 45,
  "end": 64,
  "confidence": 0.99,
  "detector": "email_regex"
}
```

Offsets are zero-based and end-exclusive. The invariant is:

```text
text[start:end] == detection["text"]
```

## Strategy selection

```mermaid
flowchart LR
    A[Candidate text] --> B{Category}
    B -->|EMAIL PHONE IP CARD| C[Regex]
    B -->|PHONE IP CARD| D[Library validation]
    B -->|PERSON COMPANY| E[spaCy NER]
    B -->|SSN ADDRESS DOB| F[Context rules]
    C --> G[Structured record]
    D --> G
    E --> G
    F --> G
```

The system favors precision safeguards at the category boundary. A date is not a DOB without DOB context, a nine-digit value is not an SSN without SSN context, and an address candidate is trimmed to the actual PII span rather than preserving surrounding prose.