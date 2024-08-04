from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 3, reader.pages

# page2_text = reader.pages[1].extract_text()  # noqa: ERA001
# assert "Table of contents" not in page2_text  # noqa: ERA001
