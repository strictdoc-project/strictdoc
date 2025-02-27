import os.path
from subprocess import CompletedProcess, TimeoutExpired, run
from typing import List, Tuple

from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.timing import measure_performance


class PDFPrintDriver:
    @staticmethod
    def get_pdf_from_html(
        project_config: ProjectConfig,
        paths_to_print: List[Tuple[str, str]],
    ) -> None:
        assert isinstance(paths_to_print, list), paths_to_print
        path_to_html2print_cache = os.path.join(
            project_config.get_path_to_cache_dir(), "html2pdf"
        )
        cmd: List[str] = [
            # Using sys.executable instead of "python" is important because
            # venv subprocess call to python resolves to wrong interpreter,
            # https://github.com/python/cpython/issues/86207
            "html2print",
            "print",
            "--cache-dir",
            path_to_html2print_cache,
        ]
        if project_config.chromedriver is not None:
            cmd.extend(
                [
                    "--chromedriver",
                    project_config.chromedriver,
                ]
            )
        for path_to_print_ in paths_to_print:
            cmd.append(path_to_print_[0])
            cmd.append(path_to_print_[1])

        with measure_performance(
            "PDFPrintDriver: printing HTML to PDF using HTML2PDF and Chrome Driver"
        ):
            try:
                _: CompletedProcess[bytes] = run(
                    cmd,
                    capture_output=False,
                    check=False,
                )
            except TimeoutExpired:
                raise TimeoutError from None
