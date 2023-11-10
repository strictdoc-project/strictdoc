from typing import List, Optional

from pybtex.database import BibliographyData, parse_file

from strictdoc.backend.sdoc.models.type_system import (
    BibEntry,
    FileEntry,
    FileEntryFormat,
)
from strictdoc.helpers.auto_described import auto_described


@auto_described
class DocumentBibliography:
    def __init__(
        self,
        parent,
        bib_files: Optional[List[FileEntry]],
        bib_entries: Optional[List[BibEntry]],
    ):
        self.parent = parent
        self.bib_db = BibliographyData()

        self.bib_files: Optional[List[FileEntry]] = bib_files
        self.bib_entries: Optional[List[BibEntry]] = bib_entries

        self.parse_bib_files(bib_files)
        self.parse_bib_entries(bib_entries)

    def parse_bib_files(self, bib_files: List[FileEntry]):
        assert bib_files is not None
        for bib_file in bib_files:
            # Only Bibtex files are supported!
            assert bib_file.g_file_format == FileEntryFormat.BIBTEX
            bibtex_db = parse_file(bib_file.g_file_path, bib_format="bibtex")
            for bib_entry in bibtex_db.entries:
                self.bib_db.add_entry(bib_entry, bibtex_db.entries[bib_entry])

    def parse_bib_entries(self, bib_entries: List[BibEntry]):
        assert bib_entries is not None
        for entry in bib_entries:
            self.bib_db.add_entry(entry.ref_cite, entry.bibtex_entry)
