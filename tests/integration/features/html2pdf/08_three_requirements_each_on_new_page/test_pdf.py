"""
@relation(SDOC-SRS-51, scope=file)
"""
import re

from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 5, reader.pages

page1_text = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX", reader.pages[0].extract_text())

assert "XXXX-XX-XX 1/5" in page1_text, page1_text

page2_text = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX", reader.pages[1].extract_text())
assert "Table of contents" in page2_text
assert "XXXX-XX-XX 2/5" in page2_text, page2_text

page3_text = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX", reader.pages[2].extract_text())
assert "Dummy high-level requirement #1" in page3_text
assert "XXXX-XX-XX 3/5" in page3_text, page3_text

page4_text = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX", reader.pages[3].extract_text())
assert "Dummy high-level requirement #2" in page4_text
assert "XXXX-XX-XX 4/5" in page4_text, page4_text

page5_text = re.sub(r"\d{4}-\d{2}-\d{2}", "XXXX-XX-XX", reader.pages[4].extract_text())
assert "Dummy high-level requirement #3" in page5_text, page5_text
assert "XXXX-XX-XX 5/5" in page5_text, page5_text
