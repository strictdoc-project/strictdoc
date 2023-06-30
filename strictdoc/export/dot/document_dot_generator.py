import os
import random
from collections import defaultdict
from pathlib import Path
from typing import List, Optional, Union

import graphviz

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import Section
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.dot.dot_templates import DotTemplates


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


class DocumentDotGenerator:
    def __init__(self, profile: str):
        assert profile in ("profile1", "profile2"), profile
        self.profile: str = profile
        self.index_template = DotTemplates.jinja_environment.get_template(
            f"{profile}/top_level.dot"
        )
        self.template_folder = DotTemplates.jinja_environment.get_template(
            f"{profile}/folder.dot"
        )
        self.template_document = DotTemplates.jinja_environment.get_template(
            f"{profile}/document.dot"
        )
        self.template_section = DotTemplates.jinja_environment.get_template(
            f"{profile}/section.dot"
        )
        self.template_requirement = DotTemplates.jinja_environment.get_template(
            f"{profile}/requirement.dot"
        )

    def export_tree(
        self, traceability_index: TraceabilityIndex, output_dot_root
    ):
        Path(output_dot_root).mkdir(parents=True, exist_ok=True)

        project_tree_content = ""

        documents_by_folder = defaultdict(list)
        for document in traceability_index.document_tree.document_list:
            if not document.has_any_requirements():
                continue
            documents_by_folder[
                document.meta.output_document_dir_rel_path
            ].append(document)

        accumulated_links = []
        accumulated_section_siblings = []
        document_flat_requirements = []
        document: Document
        for document_folder_idx, document_folder in enumerate(
            documents_by_folder.keys()
        ):
            folder_documents = documents_by_folder[document_folder]
            document_content = self._print_folder_documents(
                document_folder,
                document_folder_idx,
                folder_documents,
                accumulated_links,
                accumulated_section_siblings,
                document_flat_requirements,
            )
            project_tree_content += document_content
            project_tree_content += "\n\n"

        folders_idx = range(len(documents_by_folder))
        folder_cluster_ids = list(
            map(lambda f: f'"cluster_folder_anchor_{f}"', folders_idx)
        )
        folders_link_string = " -> ".join(folder_cluster_ids)

        def random_color():
            # https://graphviz.org/doc/info/colors.html
            return random.choice(
                [
                    "red",
                    "forestgreen",
                    "green",
                    "blue",
                    "gray10",
                    "turquoise",
                    "sienna",
                    "indigo",
                    "lightseagreen",
                    "olive",
                    "teal",
                    "webpurple",
                    "webmaroon",
                    "slateblue1",
                ]
            )

        dot_output = self.index_template.render(
            project_tree_content=project_tree_content,
            accumulated_links=accumulated_links,
            accumulated_section_siblings=accumulated_section_siblings,
            document_flat_requirements=document_flat_requirements,
            random_color=random_color,
            folders_link_string=folders_link_string,
        )

        output_path = os.path.join(
            output_dot_root, f"output.{self.profile}.dot"
        )
        with open(output_path, "w", encoding="utf8") as file:
            file.write(dot_output)

        dot = graphviz.Source.from_file(output_path)
        # view=True makes the output PDF be opened in a default viewer program.
        dot.render(output_path, view=False)

    def _print_folder_documents(
        self,
        folder_name,
        folder_idx,
        folder_documents: List[Document],
        accumulated_links,
        accumulated_section_siblings,
        document_flat_requirements,
    ):
        def get_bottom_most_section(document: Document) -> Optional[Section]:
            current_node: Union[Document, Section] = document
            candidate_section: Optional[Section] = None
            while len(current_node.section_contents) > 0:
                for subnode in reversed(current_node.section_contents):
                    if isinstance(subnode, Section):
                        candidate_section = subnode
                        current_node = subnode
                        break
                else:
                    break
            return candidate_section

        folder_documents_content = ""
        for document_idx, document in enumerate(folder_documents):
            assert document.has_any_requirements()

            document_content = self._print_document(
                document,
                folder_idx,
                document_idx,
                accumulated_links,
                accumulated_section_siblings,
                document_flat_requirements,
            )
            folder_documents_content += document_content
            folder_documents_content += "\n\n"

            if document_idx > 0:
                prev_document = folder_documents[document_idx - 1]
                prev_document_last_section = get_bottom_most_section(
                    prev_document
                )
                if prev_document_last_section is None:
                    continue

                lhs_node_id = document.section_contents[0].node_id
                if not isinstance(document.section_contents[0], Section):
                    lhs_node_id = document.node_id

                rhs_node_id = prev_document_last_section.node_id

                accumulated_section_siblings.append((lhs_node_id, rhs_node_id))

        dot_output = self.template_folder.render(
            folder_name=folder_name,
            folder_idx=folder_idx,
            folder_documents_content=folder_documents_content,
        )
        return dot_output

    def _print_document(
        self,
        document: Document,
        folder_idx,
        document_idx,
        accumulated_links,
        accumulated_section_siblings,
        document_flat_requirements,
    ) -> str:
        document_content = self._print_node(
            document, accumulated_links, accumulated_section_siblings
        )

        this_document_flat_requirements = []

        iterator = DocumentCachingIterator(document)
        for node in iterator.all_content():
            if isinstance(node, Requirement):
                uuid = self.get_requirement_uuid(node)

                this_document_flat_requirements.append(f'"value_{uuid}"')

        this_document_flat_requirements_str = (
            " -> ".join(this_document_flat_requirements)
            if len(this_document_flat_requirements) > 1
            else None
        )
        document_flat_requirements.append(this_document_flat_requirements_str)

        return self.template_document.render(
            document=document,
            document_idx=document_idx,
            folder_idx=folder_idx,
            document_content=document_content,
        )

    def _print_node(
        self,
        node: Union[Document, Section],
        accumulated_links,
        accumulated_section_siblings,
    ) -> str:
        def get_uuid(node_):
            return node_.node_id

        def get_upper_sibling_section(node_: Section):
            parent: Union[Document, Section] = node_.parent
            node_index = parent.section_contents.index(node_)
            if node_index > 0:
                candidate_upper_sibling = parent.section_contents[
                    node_index - 1
                ]
                if isinstance(candidate_upper_sibling, Section):
                    return candidate_upper_sibling
            return None

        node_content = ""
        for subnode in node.section_contents:
            if isinstance(subnode, Section):
                node_content += self._print_node(
                    subnode, accumulated_links, accumulated_section_siblings
                )
                node_content += "\n"

                upper_sibling_section = get_upper_sibling_section(subnode)
                if upper_sibling_section is not None:
                    accumulated_section_siblings.append(
                        (get_uuid(subnode), get_uuid(upper_sibling_section))
                    )
            elif isinstance(subnode, Requirement):
                node_content += self._print_requirement_fields(
                    subnode, accumulated_links
                )
                node_content += "\n"
        output = self.template_section.render(
            section=node,
            uuid=get_uuid(node),
            node_content=node_content,
            font_size=32 - node.ng_level * 4,
            context_title=f"{node.context.title_number_string} {node.title}"
            if isinstance(node, Section)
            else node.title,
        )
        return output

    def _print_requirement_fields(
        self, requirement: Requirement, accumulated_links
    ):
        def get_color_from_status(requirement_: Requirement):
            if requirement_.reserved_status is None:
                return "#87CEEB", "filled,rounded,dashed", "box", "\\l"
            if requirement_.reserved_status == "Draft":
                return "gray", "filled", "diamond", ""
            if requirement_.reserved_status == "Backlog":
                return "lightgray", "filled,rounded,dashed", "box", "\\l"
            if requirement_.reserved_status == "Progress":
                return "yellow", "filled,rounded,solid", "box", "\\l"
            if requirement_.reserved_status in ("Active", "Implemented"):
                return "white", "filled,rounded,solid", "box", "\\l"
            raise NotImplementedError(requirement.reserved_status)

        uuid = self.get_requirement_uuid(requirement)
        for parent_uid in requirement.get_parent_requirement_reference_uids():
            accumulated_links.append((uuid, parent_uid))

        output = self.template_requirement.render(
            requirement=requirement,
            uuid=uuid,
            requirement_color=get_color_from_status(requirement),
        )
        return output

    @staticmethod
    def get_requirement_uuid(requirement: Requirement):
        assert isinstance(requirement, Requirement)
        return (
            requirement.reserved_uid
            if requirement.reserved_uid is not None
            else requirement.node_id
        )
