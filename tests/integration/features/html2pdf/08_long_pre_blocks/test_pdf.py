"""
@relation(SDOC-SRS-51, scope=file)
"""

from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 4, reader.pages

page3_text = reader.pages[2].extract_text()
assert "long source content" in page3_text
assert "i++" in page3_text
