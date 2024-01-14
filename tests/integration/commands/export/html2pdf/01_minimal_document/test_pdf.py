from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

# FIXME: This must be 3. Fix when updating to a new HTML2PDF bundle.
assert len(reader.pages) == 2, reader.pages
