"""
@relation(SDOC-SRS-51, scope=file)
"""

from pypdf import PdfReader


def get_annotation_actions(path_to_pdf: str) -> list[dict]:
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
            actions.append(dict(action))
    return actions


index_actions = get_annotation_actions(
    "Output/html2pdf/pdf/index.pdf"
)
other_actions = get_annotation_actions(
    "Output/html2pdf/pdf/nested/other.pdf"
)

assert any(
    action.get("/S") == "/GoToR"
    and action.get("/F") == "nested/other.pdf"
    and action.get("/D") == "/TARGET-333"
    for action in index_actions
), index_actions

assert any(
    action.get("/S") == "/GoToR"
    and action.get("/F") == "../index.pdf"
    and action.get("/D") == "/INDEX-DOC"
    for action in other_actions
), other_actions

assert all(action.get("/S") != "/URI" for action in index_actions), index_actions
assert all(action.get("/S") != "/URI" for action in other_actions), other_actions
