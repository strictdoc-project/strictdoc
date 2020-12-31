import os


class StrictDocSemanticError(Exception):
    def __init__(
        self, title, message, example, line=None, col=None, filename=None
    ):
        self.title = title
        self.message = message
        self.example = example
        self.line = line
        self.col = col
        self.file_path = filename

    @staticmethod
    def missing_special_fields(
        special_fields, line=None, col=None, filename=None
    ):
        example_field_components = []
        for special_field in special_fields:
            example_field_components.append(
                f"- NAME: {special_field.field_name}"
            )
            example_field_components.append("  TYPE: String")
        example_field_components.append("")
        example_field_components.append("[REQUIREMENT]")
        example_field_components.append("SPECIAL_FIELDS:")
        for special_field in special_fields:
            example_field_components.append(
                f"  {special_field.field_name}: {special_field.field_value}"
            )
        example_fields = os.linesep.join(example_field_components)
        return StrictDocSemanticError(
            "Requirements special fields are not registered document-wide.",
            f"Requirement's special fields must be declared in [DOCUMENT].SPECIAL_FIELDS: {special_fields}",
            f"[DOCUMENT]\nSPECIAL_FIELDS:\n{example_fields}",
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def field_is_missing_in_doc_config(
        field_name, field_value, line=None, col=None, filename=None
    ):
        example_field_components = []
        example_field_components.append(f"- NAME: {field_name}")
        example_field_components.append("  TYPE: String")
        example_field_components.append("")
        example_field_components.append("[REQUIREMENT]")
        example_field_components.append("SPECIAL_FIELDS:")
        example_field_components.append(f"  {field_name}: {field_value}")
        example_fields = os.linesep.join(example_field_components)
        return StrictDocSemanticError(
            f"Undeclared special field: {field_name}",
            f"Requirement's special fields must be declared in [DOCUMENT].SPECIAL_FIELDS",
            f"[DOCUMENT]\nSPECIAL_FIELDS:\n{example_fields}",
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def requirement_missing_special_fields(
        special_fields_required, line=None, col=None, filename=None
    ):
        missing_special_fields = ", ".join(special_fields_required)
        example_field_components = []
        example_field_components.append("[DOCUMENT]")
        example_field_components.append("SPECIAL_FIELDS:")
        for special_field in special_fields_required:
            example_field_components.append(f"- NAME: {special_field}")
            example_field_components.append("  TYPE: String")
        example_field_components.append("")
        example_field_components.append("[REQUIREMENT]")
        example_field_components.append("SPECIAL_FIELDS:")
        for special_field in special_fields_required:
            example_field_components.append(f"  {special_field}: Some value")
        example = os.linesep.join(example_field_components)

        return StrictDocSemanticError(
            f"Requirement is missing required special fields: {missing_special_fields}",
            f"All fields that are declared in [DOCUMENT].SPECIAL_FIELDS section as 'REQUIRED: Yes' must be present in every requirement.",
            f"{example}",
            line=line,
            col=col,
            filename=filename,
        )

    @staticmethod
    def requirement_missing_required_field(
        required_special_field, line=None, col=None, filename=None
    ):
        example_field_components = []
        example_field_components.append(f"- NAME: {required_special_field}")
        example_field_components.append("  TYPE: String")
        example_field_components.append("")
        example_field_components.append("[REQUIREMENT]")
        example_field_components.append("SPECIAL_FIELDS:")
        example_field_components.append(
            f"  {required_special_field}: Some value"
        )
        example_fields = os.linesep.join(example_field_components)
        return StrictDocSemanticError(
            f"Requirement is missing a required special field: {required_special_field}.",
            f"All fields that are declared in [DOCUMENT].SPECIAL_FIELDS section as 'REQUIRED: Yes' must be present in every requirement.",
            f"[DOCUMENT]\nSPECIAL_FIELDS:\n{example_fields}",
            line=line,
            col=col,
            filename=filename,
        )

    def to_print_message(self):
        message = ""
        message += f"error: could not parse file: {self.file_path}.\n"
        message += f"Semantic error: {self.title}\n"
        message += f"Location: {self.file_path}:{self.line}:{self.col}\n"
        message += f"Message: {self.message}\n"
        message += f"Example:\n{self.example}\n"
        return message
