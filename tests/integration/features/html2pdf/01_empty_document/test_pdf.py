"""
@relation(SDOC-SRS-51, scope=file)
"""

from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 2, reader.pages

page2_text = reader.pages[1].extract_text()
assert "2/2" in page2_text
# Emoji extraction is unreliable across pypdf versions and platforms
# (depends on how the OS-provided emoji font gets embedded in the PDF),
# so only the plain text prefix is checked here.
assert "Hello world!" in page2_text
