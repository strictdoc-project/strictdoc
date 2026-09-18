import os
import posixpath
import re
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
from urllib.parse import quote, unquote, urlsplit

from strictdoc.backend.asciidoc.markup import MarkupRenderer, escape_text
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileReference,
    ParentReqReference,
)
from strictdoc.core.document_iterator import DocumentIterationContext
from strictdoc.core.format import ExportContext
from strictdoc.core.image_formats import SUPPORTED_IMAGE_FORMATS
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.file_system import file_open_read_bytes

LinkTarget = Union[SDocDocument, SDocNode, Anchor]
SAFE_UID = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")


def uid_to_anchor(uid: str) -> str:
    # Reserve sd_uid_ (StrictDoc UID) for hex-encoded UTF-8 identifiers.
    # Encode UIDs with this prefix too, so an unchanged UID cannot collide
    # with an encoded UID. Other safe UIDs remain readable in AsciiDoc links.
    if SAFE_UID.fullmatch(uid) is not None and not uid.startswith("sd_uid_"):
        return uid
    return f"sd_uid_{uid.encode('utf-8').hex()}"


class AsciiDocWriter:
    def __init__(self, context: ExportContext) -> None:
        self.context = context
        self.index = context.traceability_index
        self.documents: List[SDocDocument] = []
        self.paths: Dict[SDocDocument, Path] = {}
        self.page_content: Dict[
            SDocDocument,
            List[
                Tuple[Union[SDocDocument, SDocNode], DocumentIterationContext]
            ],
        ] = {}
        self.page_targets: Dict[SDocDocument, Set[LinkTarget]] = {}
        self.assets: Dict[Path, bytes] = {}

    def export_tree(self) -> None:
        self._collect_documents()
        for document_ in self.documents:
            self._collect_page(document_)

        rendered: Dict[Path, str] = {}
        for document_ in self.documents:
            rendered[self.paths[document_]] = self._render_page(document_)

        self._replace_output(rendered)

    def _collect_documents(self) -> None:
        seen: Set[SDocDocument] = set()
        output_paths: Set[Path] = set()

        def add_document(document: SDocDocument) -> None:
            if document in seen:
                return
            seen.add(document)
            if document.meta is None:
                raise StrictDocException(
                    f"AsciiDoc export: document has no source path: {document.title}"
                )
            relative_dir = self._safe_relative_path(
                document.meta.input_doc_dir_rel_path.relative_path,
                f"document {document.title}",
                allow_empty=True,
            )
            filename_base = self._safe_relative_path(
                document.meta.document_filename_base,
                f"document {document.title}",
            )
            if len(filename_base.parts) != 1:
                raise StrictDocException(
                    f"AsciiDoc export: invalid document filename in "
                    f"{document.title}"
                )
            output_path = relative_dir / f"{filename_base}.adoc"
            if output_path.parts[0] == "_assets":
                raise StrictDocException(
                    f"AsciiDoc export: reserved output path: {output_path}"
                )
            if output_path in output_paths:
                raise StrictDocException(
                    f"AsciiDoc export: duplicate output path: {output_path}"
                )
            output_paths.add(output_path)
            self.documents.append(document)
            self.paths[document] = output_path
            for included_ in document.included_documents:
                if not isinstance(included_, SDocDocument):
                    raise StrictDocException(
                        f"AsciiDoc export: invalid included document in {document.title}"
                    )
                add_document(included_)

        for document_ in self.index.document_tree.document_list:
            add_document(document_)

    def _collect_page(self, document: SDocDocument) -> None:
        iterator = self.index.get_document_iterator(document)
        content: List[
            Tuple[Union[SDocDocument, SDocNode], DocumentIterationContext]
        ] = []
        for item_, iteration_context_ in iterator.all_content(
            print_fragments=True
        ):
            if not isinstance(item_, (SDocDocument, SDocNode)):
                raise StrictDocException(
                    f"AsciiDoc export: unsupported document element in "
                    f"{self.paths[document]}: {type(item_).__name__}"
                )
            content.append((item_, iteration_context_))
        targets: Set[LinkTarget] = set()
        anchors: Dict[str, LinkTarget] = {}

        def add_target(target: LinkTarget, uid: Optional[str]) -> None:
            if uid is None:
                return
            anchor = uid_to_anchor(uid)
            previous = anchors.get(anchor)
            if previous is not None:
                raise StrictDocException(
                    f"AsciiDoc export: duplicate anchor [[{anchor}]] in "
                    f"{self.paths[document]}"
                )
            anchors[anchor] = target
            targets.add(target)

        add_target(document, document.uid)
        for item_, _ in content:
            if isinstance(item_, SDocDocument):
                add_target(item_, item_.uid)
            elif isinstance(item_, SDocNode):
                add_target(item_, item_.reserved_uid)
                for anchor_ in item_.get_anchors():
                    add_target(anchor_, anchor_.value)

        self.page_content[document] = content
        self.page_targets[document] = targets

    def _render_page(self, document: SDocDocument) -> str:
        output: List[str] = []
        self._render_document(document, output, level=0, page=document)
        for item_, iteration_context_ in self.page_content[document]:
            level = iteration_context_.get_level()
            if isinstance(item_, SDocDocument):
                self._render_document(item_, output, level=level, page=document)
            else:
                self._render_node(item_, output, level=level, page=document)
        return "\n\n".join(part_ for part_ in output if len(part_) > 0) + "\n"

    def _render_document(
        self,
        document: SDocDocument,
        output: List[str],
        level: int,
        page: SDocDocument,
    ) -> None:
        if level > 5:
            self._raise_depth(document, document.title)
        if document.config.get_markup() not in (
            SDocMarkup.RST,
            SDocMarkup.TEXT,
        ):
            raise StrictDocException(
                f"AsciiDoc export: unsupported source markup "
                f"{document.config.get_markup()} in "
                f"{self._context(document, 'document')}"
            )
        heading = f"{'=' * (level + 1)} {escape_text(document.title)}"
        if document.uid is not None and level > 0:
            heading = f"[[{uid_to_anchor(document.uid)}]]\n{heading}"
        output.append(heading)
        if document.uid is not None and level == 0:
            output.append(f"[[{uid_to_anchor(document.uid)}]]")
        config = document.config
        metadata: List[str] = []
        for title_, value_ in (
            ("UID", config.uid),
            ("VERSION", config.version),
            ("DATE", config.date),
            ("CLASSIFICATION", config.classification),
        ):
            if value_ is not None and len(value_) > 0:
                metadata.append(f"{title_}:: {escape_text(value_)}")

        custom_metadata = config.custom_metadata
        if custom_metadata is not None:
            for entry_ in custom_metadata.entries:
                if entry_.key is None:
                    continue
                reserved_value = {
                    "UID": config.uid,
                    "VERSION": config.version,
                    "DATE": config.date,
                    "CLASSIFICATION": config.classification,
                }.get(entry_.key.upper())
                if reserved_value is not None and len(reserved_value) > 0:
                    continue
                context = self._context(document, f"metadata {entry_.key}")
                renderer = self._renderer(page, document)
                metadata_field = SDocNodeField(
                    parent=None,
                    field_name=entry_.key,
                    parts=entry_.parts,
                    multiline__=None,
                )
                value = renderer.render(
                    metadata_field, config.get_markup(), context
                )
                metadata.append(
                    self._metadata_entry(escape_text(entry_.key), value.strip())
                )
        self._append_metadata(output, metadata)

    def _render_node(
        self,
        node: SDocNode,
        output: List[str],
        level: int,
        page: SDocDocument,
    ) -> None:
        source_document = node.get_document()
        if not isinstance(source_document, SDocDocument):
            raise StrictDocException(
                f"AsciiDoc export: node has no source document: {node.get_debug_info()}"
            )

        title = node.reserved_title
        identity = node.reserved_uid
        if identity is None:
            identity = title
        if identity is None:
            identity = node.node_type
        if node.node_type == "SECTION" and level > 5:
            self._raise_depth(
                source_document,
                title if title is not None else node.node_type,
            )
        if title is not None and node.node_type != "TEXT":
            if level > 5:
                self._raise_depth(source_document, title)
            heading = f"{'=' * (level + 1)} {escape_text(title)}"
            if node.reserved_uid is not None:
                heading = f"[[{uid_to_anchor(node.reserved_uid)}]]\n{heading}"
            if node.node_type != "SECTION":
                heading = f"[.strictdoc-requirement]\n{heading}"
            output.append(heading)
        elif node.reserved_uid is not None:
            output.append(f"[[{uid_to_anchor(node.reserved_uid)}]]")

        assert source_document.grammar is not None
        element = source_document.grammar.elements_by_type[node.node_type]
        metadata: List[str] = []
        seen_fields: Set[SDocNodeField] = set()
        field_counts: Dict[str, int] = {}
        current_fields = list(node.enumerate_fields())
        for field_ in list(node.fields_as_parsed) + current_fields:
            if field_ in seen_fields or field_ not in current_fields:
                continue
            seen_fields.add(field_)
            if (
                field_.field_name == "TITLE"
                and title is not None
                and node.node_type != "TEXT"
            ):
                continue
            occurrence = field_counts.get(field_.field_name, 0) + 1
            field_counts[field_.field_name] = occurrence
            context = self._context(
                source_document,
                f"{identity} {field_.field_name} occurrence {occurrence}",
            )
            renderer = self._renderer(page, source_document)
            if field_.field_name == node.get_content_field_name() and (
                node.node_type == "TEXT"
            ):
                self._append_metadata(output, metadata)
                output.append(
                    renderer.render(
                        field_, source_document.config.get_markup(), context
                    ).strip()
                )
                continue
            if field_.field_name in {
                source_document.config.get_relation_field(),
                "UID",
                "MID",
                "LEVEL",
            }:
                value = escape_text(field_.get_text_value())
            else:
                value = renderer.render(
                    field_, source_document.config.get_markup(), context
                ).strip()
            label = escape_text(node.get_field_human_title(field_.field_name))
            if element.is_field_multiline(field_.field_name):
                self._append_metadata(output, metadata)
                role = field_.field_name.lower().replace("_", "-")
                block = f"[.strictdoc-field.strictdoc-{role}]"
                if label != escape_text(field_.field_name):
                    block += f"\n.{label}"
                if "--" in value.splitlines():
                    raise StrictDocException(
                        f"AsciiDoc export: open block delimiter in {context}"
                    )
                output.append(f"{block}\n--\n{value}\n--")
            else:
                metadata.append(self._metadata_entry(label, value))
        self._append_metadata(output, metadata)

        for relation_ in node.relations:
            if isinstance(relation_, FileReference):
                self._append_metadata(output, metadata)
                output.append(self._render_file_relation(relation_))
                continue
            if not isinstance(
                relation_, (ParentReqReference, ChildReqReference)
            ):
                raise StrictDocException(
                    f"AsciiDoc export: unsupported relation in "
                    f"{self._context(source_document, identity)}"
                )
            target, label = self._link_target(relation_.ref_uid, page)
            role = (
                f" ({escape_text(relation_.role)})"
                if relation_.role is not None and len(relation_.role) > 0
                else ""
            )
            metadata.append(
                f"{escape_text(relation_.ref_type)}{role}:: "
                f"xref:{target}[{escape_text(label)}]"
            )

        self._append_metadata(output, metadata)

    @staticmethod
    def _append_metadata(output: List[str], metadata: List[str]) -> None:
        if len(metadata) > 0:
            body = metadata[0]
            for previous_, current_ in zip(metadata, metadata[1:]):
                separator = (
                    "\n\n" if "\n" in previous_ or "\n" in current_ else "\n"
                )
                body += separator + current_
            output.append("[.strictdoc-metadata]\n" + body)
            metadata.clear()

    @staticmethod
    def _metadata_entry(label: str, value: str) -> str:
        if "\n" in value:
            return f"{label}::\n+\n{value}"
        return f"{label}:: {value}"

    def _renderer(
        self, page: SDocDocument, source_document: SDocDocument
    ) -> MarkupRenderer:
        return MarkupRenderer(
            resolve_link=lambda link_: self._link_target(link_.link, page),
            resolve_anchor=lambda anchor_: uid_to_anchor(anchor_.value),
            resolve_image=lambda path_: self._image_path(
                path_, page, source_document
            ),
        )

    def _link_target(self, uid: str, page: SDocDocument) -> Tuple[str, str]:
        target = self.index.get_linkable_node_by_uid_weak(uid)
        if target is None:
            raise StrictDocException(
                f"AsciiDoc export: unresolved link {uid!r} in {self.paths[page]}"
            )
        if target in self.page_targets[page]:
            path = ""
        else:
            source_document = (
                target
                if isinstance(target, SDocDocument)
                else target.get_document()
            )
            if (
                not isinstance(source_document, SDocDocument)
                or source_document not in self.page_targets
            ):
                raise StrictDocException(
                    f"AsciiDoc export: link target {uid!r} is not exported"
                )
            if target not in self.page_targets[source_document]:
                raise StrictDocException(
                    f"AsciiDoc export: link target {uid!r} is filtered out"
                )
            relative_path = os.path.relpath(
                str(self.paths[source_document]),
                str(self.paths[page].parent),
            )
            path = self._quote_path(Path(relative_path))

        label = target.get_display_title(include_toc_number=False)
        return f"{path}#{uid_to_anchor(uid)}", label

    def _render_file_relation(self, relation: FileReference) -> str:
        entry = relation.g_file_entry
        details = [f"Path: {escape_text(entry.g_file_path)}"]
        descriptors = [
            ("Format", entry.g_file_format),
            ("Lines", entry.g_line_range),
        ]
        if entry.deprecated_function is not None:
            descriptors.append(("Function", entry.deprecated_function))
        elif entry.deprecated_clazz is not None:
            descriptors.append(("Class", entry.deprecated_clazz))
        else:
            descriptors.extend((("Element", entry.element), ("ID", entry.id)))
        descriptors.extend((("Hash", entry.hash), ("Role", relation.role)))
        for title_, value_ in descriptors:
            if value_ is not None and len(value_) > 0:
                details.append(f"{title_}: {escape_text(value_)}")
        return "*File:*\n\n" + "\n".join(f"* {item_}" for item_ in details)

    def _image_path(
        self, image_path: str, page: SDocDocument, source_document: SDocDocument
    ) -> str:
        try:
            decoded_path = unquote(image_path, errors="strict")
        except UnicodeDecodeError as exception:
            raise StrictDocException(
                f"AsciiDoc export: invalid image URI {image_path!r} in "
                f"{self._context(source_document, 'image')}"
            ) from exception
        try:
            image_scheme = urlsplit(decoded_path).scheme
        except ValueError as exception:
            raise StrictDocException(
                f"AsciiDoc export: invalid image URI {image_path!r} in "
                f"{self._context(source_document, 'image')}"
            ) from exception
        if len(image_scheme) > 0 or decoded_path.startswith(("/", "\\")):
            raise StrictDocException(
                f"AsciiDoc export: unsupported image path {image_path!r} "
                f"in {self._context(source_document, 'image')}"
            )
        if "?" in decoded_path or "#" in decoded_path or "\\" in decoded_path:
            raise StrictDocException(
                f"AsciiDoc export: unsupported image path {image_path!r} "
                f"in {self._context(source_document, 'image')}"
            )
        if (
            "\x00" in decoded_path
            or re.match(r"^[A-Za-z]:", decoded_path) is not None
        ):
            raise StrictDocException(
                f"AsciiDoc export: unsupported image path {image_path!r} "
                f"in {self._context(source_document, 'image')}"
            )
        relative_image = Path(decoded_path)
        assert source_document.meta is not None
        source_dir = Path(source_document.meta.input_doc_full_path).parent
        source = source_dir / relative_image
        try:
            resolved = source.resolve(strict=True)
        except (OSError, RuntimeError) as exception:
            raise StrictDocException(
                f"AsciiDoc export: missing image {image_path!r} in "
                f"{self._context(source_document, 'image')}"
            ) from exception
        if not resolved.is_file():
            raise StrictDocException(
                f"AsciiDoc export: unsupported image {image_path!r} in "
                f"{self._context(source_document, 'image')}"
            )

        input_paths = self.context.project_config.input_paths or []
        allowed = False
        for input_path_ in input_paths:
            input_root = Path(input_path_)
            if not input_root.is_dir():
                input_root = input_root.parent
            input_root_absolute = input_root.absolute()
            source_absolute = source.absolute()
            if not source_absolute.is_relative_to(input_root_absolute):
                continue
            if not resolved.is_relative_to(input_root.resolve()):
                continue
            relative_to_root = source_absolute.relative_to(input_root_absolute)
            current = input_root_absolute
            has_symlink = False
            for part_ in relative_to_root.parts:
                current /= part_
                if current.is_symlink():
                    has_symlink = True
                    break
            if not has_symlink:
                allowed = True
                break
        if not allowed:
            raise StrictDocException(
                f"AsciiDoc export: image escapes the source tree or uses a "
                f"symlink: {image_path!r}"
            )
        if resolved.suffix.lower() not in SUPPORTED_IMAGE_FORMATS:
            raise StrictDocException(
                f"AsciiDoc export: unsupported image format: {image_path!r}"
            )

        source_rel_dir = self._safe_relative_path(
            source_document.meta.input_doc_dir_rel_path.relative_path,
            self._context(source_document, "image"),
            allow_empty=True,
        )
        normalized_asset = posixpath.normpath(
            (source_rel_dir / relative_image).as_posix()
        )
        if normalized_asset in (".", "..") or normalized_asset.startswith(
            "../"
        ):
            raise StrictDocException(
                f"AsciiDoc export: image escapes the output tree: "
                f"{image_path!r}"
            )
        asset_path = Path("_assets") / normalized_asset
        if asset_path in self.paths.values():
            raise StrictDocException(
                f"AsciiDoc export: asset collides with document: {asset_path}"
            )
        with file_open_read_bytes(str(resolved)) as image_file:
            data = image_file.read()
        previous = self.assets.get(asset_path)
        if previous is not None and previous != data:
            raise StrictDocException(
                f"AsciiDoc export: conflicting image assets: {asset_path}"
            )
        self.assets[asset_path] = data
        relative_output = os.path.relpath(asset_path, self.paths[page].parent)
        return self._quote_path(Path(relative_output))

    def _replace_output(self, rendered: Dict[Path, str]) -> None:
        output_root = Path(self.context.project_config.output_dir) / "asciidoc"
        parent = output_root.parent
        parent.mkdir(parents=True, exist_ok=True)
        if output_root.is_symlink():
            raise StrictDocException(
                f"AsciiDoc export: output path is a symlink: {output_root}"
            )
        if output_root.exists():
            if not output_root.is_dir():
                raise StrictDocException(
                    f"AsciiDoc export: output path is not a directory: "
                    f"{output_root}"
                )
            for root_, dirs_, files_ in os.walk(output_root, followlinks=False):
                for name_ in dirs_ + files_:
                    child = Path(root_) / name_
                    if child.is_symlink() or not (
                        child.is_dir() or child.is_file()
                    ):
                        raise StrictDocException(
                            f"AsciiDoc export: output contains an unsafe "
                            f"entry: {child}"
                        )

        stage = Path(tempfile.mkdtemp(prefix=".asciidoc-stage-", dir=parent))
        backup = parent / f".asciidoc-backup-{uuid.uuid4().hex}"
        old_moved = False
        try:
            for path_, content_ in rendered.items():
                destination = stage / path_
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(content_, encoding="utf-8", newline="\n")
            for path_, asset_bytes_ in self.assets.items():
                destination = stage / path_
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(asset_bytes_)
            if output_root.exists():
                output_root.rename(backup)
                old_moved = True
            try:
                stage.rename(output_root)
            except OSError:
                if old_moved:
                    backup.rename(output_root)
                    old_moved = False
                raise
            if old_moved:
                shutil.rmtree(backup)
        finally:
            if stage.exists():
                shutil.rmtree(stage)

    @staticmethod
    def _safe_relative_path(
        value: str, context: str, allow_empty: bool = False
    ) -> Path:
        normalized = value.replace("\\", "/")
        if len(normalized) == 0 and allow_empty:
            return Path(".")
        if (
            len(normalized) == 0
            or normalized.startswith("/")
            or re.match(r"^[A-Za-z]:", normalized) is not None
            or "\x00" in normalized
        ):
            raise StrictDocException(
                f"AsciiDoc export: unsafe relative path {value!r} in {context}"
            )
        result = posixpath.normpath(normalized)
        if result in (".", "..") or result.startswith("../"):
            raise StrictDocException(
                f"AsciiDoc export: unsafe relative path {value!r} in {context}"
            )
        return Path(result)

    @staticmethod
    def _quote_path(path: Path) -> str:
        return "/".join(quote(part_, safe="-._~") for part_ in path.parts)

    @staticmethod
    def _context(document: SDocDocument, field: str) -> str:
        source = (
            document.meta.input_doc_full_path
            if document.meta is not None
            else document.title
        )
        return f"{source}: {field}"

    @staticmethod
    def _raise_depth(document: SDocDocument, title: str) -> None:
        raise StrictDocException(
            f"AsciiDoc export: section nesting exceeds 5 in "
            f"{AsciiDocWriter._context(document, title)}"
        )
