from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import streamlit as st

from src.detectors.unified import UnifiedDetector
from src.ingestion import extract_document
from src.normalization import normalize_text
from src.redaction import apply_redactions, redact_docx
from src.replacement import ReplacementResolver


st.set_page_config(
    page_title="PIIShield | DOCX Redaction",
    page_icon="ðŸ›¡ï¸",
    layout="wide",
)


@st.cache_resource(show_spinner=False)
def get_detector():
    """Load the spaCy-backed detector once per application instance."""

    return UnifiedDetector()


def process_document(uploaded_file):
    with TemporaryDirectory() as temporary_directory:
        workdir = Path(temporary_directory)
        source_path = workdir / "source.docx"
        output_path = workdir / "redacted.docx"
        source_path.write_bytes(uploaded_file.getvalue())

        elements = extract_document(str(source_path))
        detector = get_detector()
        resolver = ReplacementResolver()
        redacted_by_element = {}
        detections = []
        audit = []

        normalized_by_element = {
            element["element_id"]: normalize_text(element["text"])
            for element in elements
        }
        detections_by_element = detector.detect_many_fast(
            (
                normalized_by_element[element["element_id"]],
                element["element_id"],
            )
            for element in elements
        )

        for element in elements:
            element_id = element["element_id"]
            normalized = normalized_by_element[element_id]
            element_detections = detections_by_element[element_id]
            redacted_text, element_audit = apply_redactions(
                normalized,
                element_detections,
                resolver,
            )
            detections.extend(element_detections)
            audit.extend(element_audit)
            redacted_by_element[element_id] = redacted_text

        redact_docx(source_path, output_path, redacted_by_element)
        counts = Counter(item["entity_type"] for item in detections)

        return (
            output_path.read_bytes(),
            len(elements),
            len(detections),
            len(audit),
            counts,
        )


st.title("PIIShield")
st.subheader("Enterprise DOCX PII redaction")
st.write(
    "Upload a DOCX to detect nine PII categories and download a separate "
    "redacted copy. Processing is performed in the application workspace; "
    "the original file is never overwritten."
)

uploaded_file = st.file_uploader(
    "Choose a DOCX file",
    type=["docx"],
    help="Keep uploads below the hosting provider's file-size limit.",
)

if uploaded_file is not None:
    with st.spinner("Detecting and replacing sensitive values..."):
        try:
            result = process_document(uploaded_file)
        except Exception as error:  # pragma: no cover - UI safety boundary
            st.error(f"The document could not be processed: {error}")
        else:
            redacted_bytes, elements, candidates, redactions, counts = result

            metric_columns = st.columns(4)
            metric_columns[0].metric("Elements", elements)
            metric_columns[1].metric("Candidates", candidates)
            metric_columns[2].metric("Redactions", redactions)
            metric_columns[3].metric("Categories", len(counts))

            if counts:
                summary = pd.DataFrame(
                    sorted(
                        counts.items(),
                        key=lambda item: item[0],
                    ),
                    columns=["Entity type", "Occurrences"],
                )
                st.dataframe(summary, hide_index=True, use_container_width=True)
            else:
                st.info("No supported PII values were detected in this file.")

            output_name = f"redacted_{uploaded_file.name}"
            st.download_button(
                "Download redacted DOCX",
                data=redacted_bytes,
                file_name=output_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
            )

st.divider()
st.caption(
    "Supported categories: PERSON, EMAIL, PHONE, COMPANY, ADDRESS, SSN, "
    "CREDIT_CARD, DOB, and IP_ADDRESS."
)

