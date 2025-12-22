"""
@relation(SDOC-SRS-51, scope=file)
"""

from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 5, reader.pages

page1_text = reader.pages[0].extract_text()
assert "2025-12-23 1/5" in page1_text, page1_text

page2_text = reader.pages[1].extract_text()
assert "Table of contents" in page2_text
assert "2025-12-23 2/5" in page2_text, page2_text

page3_text = reader.pages[2].extract_text()
assert "Dummy high-level requirement #1" in page3_text
assert "2025-12-23 3/5" in page3_text, page3_text

page4_text = reader.pages[3].extract_text()
assert "Dummy high-level requirement #2" in page4_text
assert "2025-12-23 4/5" in page4_text, page4_text

page5_text = reader.pages[4].extract_text()
assert "Dummy high-level requirement #3" in page5_text, page5_text
assert "2025-12-23 5/5" in page5_text, page5_text
