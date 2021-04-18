class DocumentMeta:
    def __init__(
        self,
        level,
        document_filename_base,
        input_doc_full_path,
        input_doc_dir_rel_path,
        output_document_dir_full_path,
        output_document_dir_rel_path,
    ):
        self.level = level
        self.document_filename_base = document_filename_base
        self.input_doc_full_path = input_doc_full_path
        self.input_doc_rel_path = input_doc_dir_rel_path
        self.output_document_dir_full_path = output_document_dir_full_path
        self.output_document_dir_rel_path = output_document_dir_rel_path

    # Paths
    def get_html_doc_path(self):
        return "{}/{}.html".format(
            self.output_document_dir_full_path, self.document_filename_base
        )

    def get_html_doc_standalone_path(self):
        return "{}/{}.standalone.html".format(
            self.output_document_dir_full_path, self.document_filename_base
        )

    def get_html_table_path(self):
        return "{}/{} - TABLE.html".format(
            self.output_document_dir_full_path, self.document_filename_base
        )

    def get_html_traceability_path(self):
        return "{}/{} - TRACE.html".format(
            self.output_document_dir_full_path, self.document_filename_base
        )

    def get_html_deep_traceability_path(self):
        return "{}/{} - DEEP-TRACE.html".format(
            self.output_document_dir_full_path, self.document_filename_base
        )

    # Links
    def get_html_doc_link(self):
        return "{}/{}.html".format(
            self.output_document_dir_rel_path, self.document_filename_base
        )

    def get_html_table_link(self):
        return "{}/{} - TABLE.html".format(
            self.output_document_dir_rel_path, self.document_filename_base
        )

    def get_html_traceability_link(self):
        return "{}/{} - TRACE.html".format(
            self.output_document_dir_rel_path, self.document_filename_base
        )

    def get_html_deep_traceability_link(self):
        return "{}/{} - DEEP-TRACE.html".format(
            self.output_document_dir_rel_path, self.document_filename_base
        )

    def get_html_link(self, document_type, other_doc_level):
        path_prefix = self.get_root_path_prefix(other_doc_level)
        if document_type == "document":
            document_link = self.get_html_doc_link()
        elif document_type == "table":
            document_link = self.get_html_table_link()
        elif document_type == "trace":
            document_link = self.get_html_traceability_link()
        elif document_type == "deeptrace":
            document_link = self.get_html_deep_traceability_link()
        else:
            raise NotImplementedError
        return f"{path_prefix}/{document_link}"

    def get_root_path_prefix(self, other_doc_level=None):
        level = self.level if not other_doc_level else other_doc_level
        if level == 0:
            return ".."
        return ("../" * level)[:-1]
