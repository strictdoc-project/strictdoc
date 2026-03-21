"""
@relation(SDOC-SRS-51, scope=file)
"""

import ntpath
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote, urlsplit

from pypdf import PdfWriter
from pypdf.generic import (
    DictionaryObject,
    NameObject,
    PdfObject,
    TextStringObject,
)


class PDFPostprocessor:
    @classmethod
    def rewrite_cross_document_links(
        cls,
        *,
        path_to_input_root: str,  # noqa: ARG003
        paths_to_print: List[Tuple[str, str]],
    ) -> None:
        html_to_pdf_map: Dict[str, str] = {
            urlsplit(
                Path(path_to_html).resolve().as_uri()
            ).path: os.path.abspath(path_to_pdf)
            for path_to_html, path_to_pdf in paths_to_print
        }
        for _, path_to_pdf in paths_to_print:
            cls._rewrite_cross_document_links_in_single_document(
                html_to_pdf_map=html_to_pdf_map,
                path_to_pdf=path_to_pdf,
            )

    @classmethod
    def _rewrite_cross_document_links_in_single_document(
        cls,
        *,
        html_to_pdf_map: Dict[str, str],
        path_to_pdf: str,
    ) -> None:
        path_to_pdf = os.path.abspath(path_to_pdf)
        path_to_pdf_dir = os.path.dirname(path_to_pdf)

        writer = PdfWriter(clone_from=path_to_pdf)
        modified = False

        for page in writer.pages:
            annotations = page.get("/Annots")
            if annotations is None:
                continue

            for annotation_reference in annotations:
                annotation = annotation_reference.get_object()
                if not isinstance(annotation, DictionaryObject):
                    continue
                if annotation.get("/Subtype") != "/Link":
                    continue

                action = annotation.get("/A")
                if not isinstance(action, DictionaryObject):
                    continue
                if action.get("/S") != "/URI":
                    continue

                uri = action.get("/URI")
                if not isinstance(uri, str):
                    continue

                rewritten_action = cls._create_pdf_gotor_action(
                    uri=uri,
                    html_to_pdf_map=html_to_pdf_map,
                    path_to_pdf_dir=path_to_pdf_dir,
                )
                if rewritten_action is None:
                    continue

                annotation[NameObject("/A")] = rewritten_action
                modified = True

        if not modified:
            return

        with NamedTemporaryFile(
            mode="wb",
            suffix=".pdf",
            dir=path_to_pdf_dir,
            delete=False,
        ) as temp_file:
            writer.write(temp_file)
            temp_file_path = temp_file.name
        os.replace(temp_file_path, path_to_pdf)

    @staticmethod
    def _create_pdf_gotor_action(
        *,
        uri: str,
        html_to_pdf_map: Dict[str, str],
        path_to_pdf_dir: str,
    ) -> Optional[DictionaryObject]:
        # ruff: noqa: ERA001
        # urlsplit() produces an object of the following kind:
        # SplitResult(
        #     scheme='file',
        #     netloc='',
        #     path='<path-to-project>/output/html2pdf/html/<project-mount-folder>/<path-to-doc>-PDF.html',
        #     query='',
        #     fragment='ANCHOR'
        # )
        parsed_uri = urlsplit(uri)
        if parsed_uri.scheme != "file":
            return None

        matching_pdf_abspath = html_to_pdf_map.get(parsed_uri.path)
        if matching_pdf_abspath is None:
            return None

        matching_pdf_relpath = PDFPostprocessor._create_relative_pdf_path(
            path_to_pdf=matching_pdf_abspath,
            start_dir=path_to_pdf_dir,
        )

        action = DictionaryObject()
        action[NameObject("/Type")] = NameObject("/Action")
        action[NameObject("/S")] = NameObject("/GoToR")
        action[NameObject("/F")] = TextStringObject(matching_pdf_relpath)

        destination_name = unquote(parsed_uri.fragment)
        if destination_name is not None and len(destination_name) > 0:
            action[NameObject("/D")] = (
                PDFPostprocessor._create_destination_object(destination_name)
            )
        return action

    @staticmethod
    def _create_destination_object(destination_name: str) -> PdfObject:
        assert len(destination_name) > 0
        if destination_name.startswith("/"):
            return NameObject(destination_name)
        return NameObject(f"/{destination_name}")

    @staticmethod
    def _create_relative_pdf_path(*, path_to_pdf: str, start_dir: str) -> str:
        path_module = (
            ntpath
            if ntpath.splitdrive(path_to_pdf)[0]
            or ntpath.splitdrive(start_dir)[0]
            else os.path
        )
        relative_path = path_module.relpath(path_to_pdf, start=start_dir)
        # assert is needed to satisfy the type checker.
        assert isinstance(relative_path, str), relative_path
        return relative_path.replace("\\", "/")
