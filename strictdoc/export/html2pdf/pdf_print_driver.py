from subprocess import CompletedProcess, TimeoutExpired, run

from strictdoc import environment
from strictdoc.helpers.timing import measure_performance


class PDFPrintDriver:
    @staticmethod
    def get_pdf_from_html(path_to_input_html, path_to_output_pdf):
        with measure_performance(
            "PDFPrintDriver: printing HTML to PDF using HTML2PDF and Chrome Driver"
        ):
            try:
                _: CompletedProcess = run(
                    [
                        "python",
                        environment.get_path_to_html2pdf(),
                        path_to_input_html,
                        path_to_output_pdf,
                    ],
                    capture_output=False,
                    timeout=15,
                    check=False,
                )
            except TimeoutExpired:
                raise TimeoutError from None
