from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/bundle.pdf")

assert len(reader.pages) == 3, reader.pages
