class DocumentMeta:
    def __init__(self,
                 level,
                 document_filename_base,
                 input_doc_full_path,
                 output_document_dir_full_path,
                 output_document_dir_rel_path):
        self.level = level
        self.document_filename_base = document_filename_base
        self.input_doc_full_path = input_doc_full_path
        self.output_document_dir_full_path = output_document_dir_full_path
        self.output_document_dir_rel_path = output_document_dir_rel_path

    # Paths
    def get_html_doc_path(self):
        return "{}/{}.html".format(self.output_document_dir_full_path,
                                   self.document_filename_base)

    def get_html_table_path(self):
        return "{}/{} - TABLE.html".format(self.output_document_dir_full_path,
                                           self.document_filename_base)

    def get_html_traceability_path(self):
        return "{}/{} - TRACE.html".format(self.output_document_dir_full_path,
                                           self.document_filename_base)

    def get_html_deep_traceability_path(self):
        return "{}/{} - DEEP-TRACE.html".format(self.output_document_dir_full_path,
                                                self.document_filename_base)

    # Links
    def get_html_doc_link(self):
        return "{}/{}.html".format(self.output_document_dir_rel_path,
                                   self.document_filename_base)

    def get_html_table_link(self):
        return "{}/{} - TABLE.html".format(self.output_document_dir_rel_path,
                                           self.document_filename_base)

    def get_html_traceability_link(self):
        return "{}/{} - TRACE.html".format(self.output_document_dir_rel_path,
                                           self.document_filename_base)

    def get_html_deep_traceability_link(self):
        return "{}/{} - DEEP-TRACE.html".format(self.output_document_dir_rel_path,
                                                self.document_filename_base)

    def get_root_path_prefix(self):
        assert self.level > 0
        return ('../' * self.level)[:-1]
