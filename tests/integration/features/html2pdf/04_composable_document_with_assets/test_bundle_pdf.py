# @relation(SDOC-SRS-51, scope=file)

from pypdf import PdfReader

reader = PdfReader("Output/html2pdf/pdf/bundle.pdf")

assert len(reader.pages) == 5, reader.pages
