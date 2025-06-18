# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import re
from collections import defaultdict
from typing import Dict, List, Optional

from markupsafe import Markup
from starlette.datastructures import FormData

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.form_data import ParsedFormData, parse_form_data
from strictdoc.helpers.string import sanitize_html_form_field
from strictdoc.server.error_object import ErrorObject
from strictdoc.server.helpers.turbo import render_turbo_stream


@auto_described
class IncludedDocumentFormObject(ErrorObject):
    def __init__(
        self,
        *,
        document_mid: str,
        context_document_mid: str,
        document_title: str,
        jinja_environment: JinjaEnvironment,
    ) -> None:
        assert isinstance(document_mid, str), document_mid
        assert isinstance(context_document_mid, str), context_document_mid
        assert isinstance(document_title, str), document_title
        super().__init__()
        self.document_mid: Optional[str] = document_mid
        self.context_document_mid: Optional[str] = context_document_mid
        self.document_title: str = document_title
        self.jinja_environment: JinjaEnvironment = jinja_environment

    @staticmethod
    def create_from_request(
        *, request_form_data: FormData, jinja_environment: JinjaEnvironment
    ) -> "IncludedDocumentFormObject":
        request_form_data_as_list = [
            (field_name, field_value)
            for field_name, field_value in request_form_data.multi_items()
        ]
        request_form_dict: ParsedFormData = assert_cast(
            parse_form_data(request_form_data_as_list), dict
        )
        document_mid: str = assert_cast(request_form_dict["document_mid"], str)
        context_document_mid: str = assert_cast(
            request_form_dict["context_document_mid"], str
        )

        # FIXME: Rewrite the legacy way of parsing by also use data from
        #        request_form_dict above.
        config_fields: Dict[str, List[str]] = defaultdict(list)
        for field_name, field_value in request_form_data.multi_items():
            result = re.search(r"^document\[(.*)]$", field_name)
            if result is not None:
                config_fields[result.group(1)].append(field_value)
        document_title: str = (
            config_fields["TITLE"][0] if "TITLE" in config_fields else ""
        )
        document_title = sanitize_html_form_field(
            document_title, multiline=False
        )
        document_title = document_title if document_title is not None else ""

        form_object = IncludedDocumentFormObject(
            document_mid=document_mid,
            context_document_mid=context_document_mid,
            document_title=document_title,
            jinja_environment=jinja_environment,
        )
        return form_object

    @staticmethod
    def create_from_document(
        *,
        document: SDocDocument,
        context_document_mid: str,
        jinja_environment: JinjaEnvironment,
    ) -> "IncludedDocumentFormObject":
        assert isinstance(document, SDocDocument)

        return IncludedDocumentFormObject(
            document_mid=document.reserved_mid,
            context_document_mid=context_document_mid,
            document_title=document.title,
            jinja_environment=jinja_environment,
        )

    def render_edit_form(self) -> Markup:
        rendered_template = self.jinja_environment.render_template_as_markup(
            "components/included_document_form/index.jinja", form_object=self
        )
        return render_turbo_stream(
            content=rendered_template,
            action="replace",
            target=f"article-{self.document_mid}",
        )
