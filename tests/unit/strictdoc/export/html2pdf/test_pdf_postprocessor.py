from pathlib import Path
from urllib.parse import urlsplit

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    TextStringObject,
)

from strictdoc.export.html2pdf.pdf_postprocessor import PDFPostprocessor


def test_pdf_postprocessor_rewrites_export_local_file_uris(
    tmp_path: Path,
) -> None:
    export_root = tmp_path / "Output" / "html2pdf"
    html_root = export_root / "html"
    pdf_root = export_root / "pdf"

    source_html = html_root / "docs" / "source-PDF.html"
    target_html = html_root / "docs" / "nested" / "other-PDF.html"
    skipped_html = html_root / "docs" / "skipped-PDF.html"
    external_html = tmp_path / "outside" / "outside-PDF.html"
    source_pdf = pdf_root / "docs" / "source.pdf"
    target_pdf = pdf_root / "docs" / "nested" / "other.pdf"

    for path in (
        source_html,
        target_html,
        skipped_html,
        external_html,
        source_pdf,
        target_pdf,
    ):
        path.parent.mkdir(parents=True, exist_ok=True)

    source_html.write_text("", encoding="utf8")
    target_html.write_text("", encoding="utf8")
    skipped_html.write_text("", encoding="utf8")
    external_html.write_text("", encoding="utf8")

    _create_pdf_with_link_annotations(
        path_to_pdf=source_pdf,
        uris=(
            target_html.resolve().as_uri() + "#OTHER-DOC",
            skipped_html.resolve().as_uri() + "#SKIPPED-DOC",
            "https://example.com/strictdoc",
            external_html.resolve().as_uri() + "#OUTSIDE-DOC",
        ),
    )
    _create_pdf_with_link_annotations(
        path_to_pdf=target_pdf,
        uris=(source_html.resolve().as_uri() + "#SOURCE-DOC",),
    )

    PDFPostprocessor.rewrite_cross_document_links(
        path_to_input_root=str(html_root),
        paths_to_print=[
            (str(source_html), str(source_pdf)),
            (str(target_html), str(target_pdf)),
        ],
    )

    actions = _read_pdf_annotation_actions(path_to_pdf=source_pdf)

    assert actions[0]["/S"] == "/GoToR"
    assert actions[0]["/F"] == "nested/other.pdf"
    assert actions[0]["/D"] == "/OTHER-DOC"

    assert actions[1]["/S"] == "/URI"
    assert (
        actions[1]["/URI"] == skipped_html.resolve().as_uri() + "#SKIPPED-DOC"
    )

    assert actions[2]["/S"] == "/URI"
    assert actions[2]["/URI"] == "https://example.com/strictdoc"

    assert actions[3]["/S"] == "/URI"
    assert (
        actions[3]["/URI"] == external_html.resolve().as_uri() + "#OUTSIDE-DOC"
    )

    backlink_actions = _read_pdf_annotation_actions(path_to_pdf=target_pdf)

    assert backlink_actions[0]["/S"] == "/GoToR"
    assert backlink_actions[0]["/F"] == "../source.pdf"
    assert backlink_actions[0]["/D"] == "/SOURCE-DOC"


def test_pdf_postprocessor_rewrites_windows_relative_paths_with_slashes() -> (
    None
):
    html_uri = "file:///C:/project/Output/html2pdf/html/docs/source-PDF.html"

    action = PDFPostprocessor._create_pdf_gotor_action(
        uri=html_uri + "#SOURCE-DOC",
        html_to_pdf_map={
            urlsplit(html_uri).path: (
                r"C:\project\Output\html2pdf\pdf\docs\source.pdf"
            )
        },
        path_to_pdf_dir=r"C:\project\Output\html2pdf\pdf\docs\nested",
    )

    assert action is not None
    assert action["/S"] == "/GoToR"
    assert action["/F"] == "../source.pdf"
    assert action["/D"] == "/SOURCE-DOC"


def _create_pdf_with_link_annotations(
    *, path_to_pdf: Path, uris: tuple[str, ...]
) -> None:
    writer = PdfWriter()
    page = writer.add_blank_page(width=200, height=200)

    annotations = ArrayObject()
    for uri in uris:
        annotation = DictionaryObject()
        annotation[NameObject("/Type")] = NameObject("/Annot")
        annotation[NameObject("/Subtype")] = NameObject("/Link")
        annotation[NameObject("/Rect")] = ArrayObject(
            [
                NumberObject(0),
                NumberObject(0),
                NumberObject(10),
                NumberObject(10),
            ]
        )
        annotation[NameObject("/Border")] = ArrayObject(
            [NumberObject(0), NumberObject(0), NumberObject(0)]
        )

        action = DictionaryObject()
        action[NameObject("/Type")] = NameObject("/Action")
        action[NameObject("/S")] = NameObject("/URI")
        action[NameObject("/URI")] = TextStringObject(uri)

        annotation[NameObject("/A")] = action
        annotations.append(writer._add_object(annotation))

    page[NameObject("/Annots")] = annotations

    with path_to_pdf.open("wb") as output_file:
        writer.write(output_file)


def _read_pdf_annotation_actions(
    *, path_to_pdf: Path
) -> list[DictionaryObject]:
    reader = PdfReader(path_to_pdf)
    actions = []
    for page in reader.pages:
        annotations = page.get("/Annots")
        if annotations is None:
            continue
        for annotation_reference in annotations:
            annotation = annotation_reference.get_object()
            action = annotation.get("/A")
            if action is None:
                continue
            actions.append(action)
    return actions
