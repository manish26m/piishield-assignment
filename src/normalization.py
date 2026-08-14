
from pathlib import Path
import json
import re
import unicodedata

import pandas as pd


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode characters while preserving readable text.
    """
    return unicodedata.normalize("NFKC", text)


def normalize_whitespace(text: str) -> str:
    """
    Normalize repeated whitespace without destroying the original text.
    """
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


def normalize_text(text: str) -> str:
    """
    Apply all text normalization operations.
    """
    text = normalize_unicode(text)
    text = normalize_whitespace(text)

    return text


def load_bronze(input_path: str) -> list:
    """
    Load Bronze JSONL records.
    """
    records = []

    with open(input_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def create_silver_dataframe(records: list) -> pd.DataFrame:
    """
    Convert Bronze records into the Silver representation.
    """

    silver_records = []

    for record in records:

        original_text = record["text"]
        normalized_text = normalize_text(original_text)

        silver_record = record.copy()

        # Preserve raw text
        silver_record["original_text"] = original_text

        # Add normalized representation
        silver_record["normalized_text"] = normalized_text

        silver_records.append(silver_record)

    return pd.DataFrame(silver_records)


def save_silver(df: pd.DataFrame, output_path: str):
    """
    Save Silver data as Parquet.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(
        output_path,
        engine="pyarrow",
        index=False
    )


if __name__ == "__main__":

    project_root = Path(__file__).resolve().parent.parent

    bronze_path = (
        project_root
        / "data"
        / "bronze"
        / "document_elements.jsonl"
    )

    silver_path = (
        project_root
        / "data"
        / "silver"
        / "normalized_elements.parquet"
    )

    print("Starting Silver-layer transformation...")
    print(f"Bronze input: {bronze_path}")

    # Load Bronze
    records = load_bronze(str(bronze_path))

    print(f"Bronze records loaded: {len(records)}")

    # Transform
    df = create_silver_dataframe(records)

    # Save
    save_silver(df, str(silver_path))

    print()
    print("Silver transformation complete.")
    print(f"Silver records: {len(df)}")
    print(f"Silver output: {silver_path}")