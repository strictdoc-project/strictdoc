from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/input.pdf")

assert len(reader.pages) == 5, reader.pages
