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


def test_get_custom_metadata_excludes_entry_present_in_config():
    config = DocumentConfig.default_config(document=None)
    config.uid = "DOC-1"
    config.custom_metadata = DocumentCustomMetadata(
        entries=[
            DocumentCustomMetadataKeyValuePair(key="UID", value="DOC-1"),
            DocumentCustomMetadataKeyValuePair(key="Author", value="Jane"),
        ]
    )

    assert config.get_custom_metadata() == [("Author", "Jane")]


def test_get_custom_metadata_keeps_entry_not_present_in_config():
    config = DocumentConfig.default_config(document=None)
    config.custom_metadata = DocumentCustomMetadata(
        entries=[
            DocumentCustomMetadataKeyValuePair(key="UID", value="DOC-1"),
        ]
    )

    assert config.get_custom_metadata() == [("UID", "DOC-1")]
