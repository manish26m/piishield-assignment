
from src.access_control import AccessController
from src.security import PIISecurity


def test_security_hash_and_token_are_stable():
    security = PIISecurity("test-secret")

    assert security.hash_value("same") == security.hash_value("same")
    assert security.tokenize("same") == security.tokenize("same")
    assert security.tokenize("same") != security.tokenize("different")


def test_security_masks_sensitive_values():
    security = PIISecurity()

    assert security.mask_value("user@example.com", "EMAIL") == "u***@example.com"
    assert security.mask_value("4111 1111 1111 1111", "CREDIT_CARD").endswith("1111")
    assert security.generalize_ip("192.168.1.10") == "192.168.0.0/16"


def test_access_controller_records_granted_and_denied_access():
    controller = AccessController()

    granted = controller.record_access(
        "analyst-1",
        "analyst",
        "read_redacted",
        "data/gold/redacted_entities.parquet",
    )
    denied = controller.record_access(
        "viewer-1",
        "viewer",
        "read_original",
        "data/bronze/document_elements.jsonl",
    )

    assert granted["access_granted"] is True
    assert denied["access_granted"] is False
    assert len(controller.records) == 2