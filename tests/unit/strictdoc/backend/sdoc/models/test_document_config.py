from strictdoc.backend.sdoc.models.document_config import (
    DocumentConfig,
    DocumentCustomMetadata,
    DocumentCustomMetadataKeyValuePair,
)


def test_has_custom_metadata_returns_false_when_entries_are_empty():
    config = DocumentConfig.default_config(document=None)
    config.custom_metadata = DocumentCustomMetadata(entries=[])
    assert config.has_custom_metadata() is False


def test_has_custom_metadata_returns_true_when_entries_are_present():
    config = DocumentConfig.default_config(document=None)
    config.custom_metadata = DocumentCustomMetadata(
        entries=[
            DocumentCustomMetadataKeyValuePair(key="FOO", value="bar"),
        ]
    )
    assert config.has_custom_metadata() is True


def test_has_custom_metadata_returns_false_when_no_custom_metadata():
    config = DocumentConfig.default_config(document=None)
    assert config.has_custom_metadata() is False
