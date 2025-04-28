from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.paths import SDocRelativePath


def create_fake_document_meta():
    return DocumentMeta(
        level=1,
        file_tree_mount_folder="root_folder",
        document_filename="fake_doc.sdoc",
        document_filename_base="fake_doc",
        input_doc_full_path="/tmp/root_folder/fake_doc.sdoc",
        input_doc_rel_path=SDocRelativePath("fake_doc.sdoc"),
        input_doc_dir_rel_path=SDocRelativePath(""),
        input_doc_assets_dir_rel_path=SDocRelativePath("_assets"),
        output_document_dir_full_path="/tmp/output/root_folder/",
        output_document_dir_rel_path=SDocRelativePath(""),
    )
