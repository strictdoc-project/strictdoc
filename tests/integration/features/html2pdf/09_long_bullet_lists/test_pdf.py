"""
@relation(SDOC-SRS-51, scope=file)
"""

from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 6, reader.pages

page3_text = reader.pages[2].extract_text()
assert "CRA Annex I:" in page3_text, page3_text
