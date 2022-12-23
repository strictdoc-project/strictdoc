from typing import Optional, List

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

        self.bib_files = bib_files
        self.bib_entries = bib_entries

        self.parse_bib_files(bib_files)
        self.parse_bib_entries(bib_entries)

    def parse_bib_entries(self, bib_entries):
        if bib_entries and len(bib_entries) > 0:
            for entry in bib_entries:
                self.bib_db.add_entry(entry.ref_cite, entry.bibtex_entry)

    def parse_bib_files(self, bib_files):
        if bib_files and len(bib_files) > 0:
            for bib_file in bib_files:
                assert bib_file.file_format == FileEntryFormat.BIBTEX
                # Only Bibtex files are suppported!
                bibtex_db = parse_file(bib_file.file_path, bib_format="bibtex")
                for bib_entry in bibtex_db.entries:
                    self.bib_db.add_entry(
                        bib_entry, bibtex_db.entries[bib_entry]
                    )
