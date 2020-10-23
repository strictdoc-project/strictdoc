class DocumentMeta:
    def __init__(self,
                 level,
                 sdoc_full_path,
                 output_folder_rel_path,
                 rel_out_path,
                 filenamebase):
        self.level = level
        self.sdoc_full_path = sdoc_full_path
        self.output_folder_rel_path = output_folder_rel_path
        self.rel_out_path = rel_out_path
        self.filenamebase = filenamebase

    def get_html_doc_path(self):
        return "{}/{}.html".format(self.output_folder_rel_path,
                                   self.filenamebase)

    def get_html_table_path(self):
        return "{}/{} - TABLE.html".format(self.output_folder_rel_path,
                                           self.filenamebase)

    def get_html_traceability_path(self):
        return "{}/{} - TRACE.html".format(self.output_folder_rel_path,
                                           self.filenamebase)

    def get_html_deep_traceability_path(self):
        return "{}/{} - DEEP-TRACE.html".format(self.output_folder_rel_path,
                                                self.filenamebase)

    def get_html_doc_link(self):
        return "{}/{}.html".format(self.rel_out_path,
                                   self.filenamebase)

    def get_html_table_link(self):
        return "{}/{} - TABLE.html".format(self.rel_out_path,
                                           self.filenamebase)

    def get_html_traceability_link(self):
        return "{}/{} - TRACE.html".format(self.rel_out_path,
                                           self.filenamebase)

    def get_html_deep_traceability_link(self):
        return "{}/{} - DEEP-TRACE.html".format(self.rel_out_path,
                                                self.filenamebase)

    def get_root_path_prefix(self):
        assert self.level > 0
        return ('../' * self.level)[:-1]
