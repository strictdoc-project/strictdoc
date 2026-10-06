import datetime
import glob
import hashlib
import os.path
import shutil
import tempfile
from pathlib import Path
from typing import Any, List, Optional

import jinja2
from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    ModuleLoader,
    StrictUndefined,
    Template,
)
from markupsafe import Markup

from strictdoc import environment
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.jinja.assert_extension import AssertExtension
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.timing import measure_performance


class JinjaEnvironment:
    environment: Environment

    def __init__(self, environment: Environment):
        self.environment = environment

    def get_template(self, *args: Any, **kwargs: Any) -> Template:
        return self.environment.get_template(*args, **kwargs)

    def render_template_as_markup(
        self, template: str, *args: Any, **kwargs: Any
    ) -> Markup:
        return Markup(
            self.environment.get_template(template).render(*args, **kwargs)
        )


class HTMLTemplates:
    @staticmethod
    def create(
        project_config: ProjectConfig,
        enable_caching: bool,
        strictdoc_last_update: datetime.datetime,
    ) -> "HTMLTemplates":
        assert isinstance(strictdoc_last_update, datetime.datetime)
        if enable_caching:
            cacheable_templates = CompiledHTMLTemplates(project_config)
            cacheable_templates.reset_jinja_environment_if_outdated(
                strictdoc_last_update
            )
            cacheable_templates.compile_jinja_templates()
            return CompiledHTMLTemplates(project_config)

        return NormalHTMLTemplates()

    def jinja_environment(self) -> JinjaEnvironment:
        raise NotImplementedError


class NormalHTMLTemplates(HTMLTemplates):
    def __init__(self) -> None:
        self._jinja_environment: JinjaEnvironment = JinjaEnvironment(
            Environment(
                loader=FileSystemLoader(
                    environment.get_path_to_html_templates()
                ),
                undefined=StrictUndefined,
                extensions=[AssertExtension],
                autoescape=True,
            )
        )

    def jinja_environment(self) -> JinjaEnvironment:
        return self._jinja_environment


class CompiledHTMLTemplates(HTMLTemplates):
    """
    Jinja templates precompiled to Python modules in the cache folder.

    A cache bucket is used only if it is complete: it is compiled into a
    temporary folder that is renamed into place when done, and it carries a
    marker file with a fingerprint of the template files it was compiled
    from. A bucket without a matching marker (a run stopped mid-compile, or
    the cache of another StrictDoc build with the same version number) is
    compiled again. This matters most for binary distributions (PyInstaller),
    where reset_jinja_environment_if_outdated() never fires because there are
    no StrictDoc source files to compare the cache against.
    """

    COMPLETE_MARKER = "strictdoc_compiled_templates.txt"

    def __init__(self, project_config: ProjectConfig):
        path_to_output_dir_hash = hashlib.md5(
            project_config.output_dir.encode("utf-8")
        ).hexdigest()
        # Absolute, because ModuleLoader imports the compiled templates from
        # this path whenever a template is first used, and a relative path
        # (the server's default output dir is "./output/server") would be
        # resolved against whatever the current directory is at that time.
        self.path_to_jinja_cache_bucket_dir = os.path.abspath(
            os.path.join(
                project_config.get_path_to_cache_dir(),
                "jinja",
                path_to_output_dir_hash,
            )
        )
        self._jinja_environment: Optional[JinjaEnvironment] = None

    @staticmethod
    def get_templates_fingerprint() -> str:
        """
        Identify the template files (and the Jinja version) a compiled cache
        was made from, cheaply: names, sizes and modification times.
        """
        hasher = hashlib.sha256(jinja2.__version__.encode("utf-8"))
        for path_to_templates in environment.get_path_to_html_templates():
            for root, dirs, files in os.walk(path_to_templates):
                dirs.sort()
                for file_name in sorted(files):
                    path_to_file = os.path.join(root, file_name)
                    stat = os.stat(path_to_file)
                    hasher.update(
                        (
                            f"{os.path.relpath(path_to_file, path_to_templates)}"
                            f":{stat.st_size}:{stat.st_mtime_ns}\n"
                        ).encode()
                    )
        return hasher.hexdigest()

    def is_jinja_cache_complete(self, fingerprint: str) -> bool:
        path_to_marker = os.path.join(
            self.path_to_jinja_cache_bucket_dir, self.COMPLETE_MARKER
        )
        try:
            with open(path_to_marker, encoding="utf-8") as marker_file:
                return marker_file.read().strip() == fingerprint
        except OSError:
            return False

    def compile_jinja_templates(self) -> None:
        fingerprint = self.get_templates_fingerprint()
        if self.is_jinja_cache_complete(fingerprint):
            return
        # Incomplete or outdated: compile it again from scratch.
        shutil.rmtree(self.path_to_jinja_cache_bucket_dir, ignore_errors=True)

        jinja_environment = Environment(
            loader=FileSystemLoader(environment.get_path_to_html_templates()),
            undefined=StrictUndefined,
            extensions=[AssertExtension],
            autoescape=True,
        )
        # TODO: Check if this line is still needed (might be some older workaround).
        jinja_environment.globals.update(isinstance=isinstance)
        with measure_performance("Compile Jinja templates"):

            def filter_function_(name: str) -> bool:
                # On macOS, the .DS_Store files make Jinja templates compiler
                # to crash.
                # https://github.com/strictdoc-project/strictdoc/issues/1266
                if name.endswith(".DS_Store"):
                    return False
                return True

            path_to_parent_dir = os.path.dirname(
                self.path_to_jinja_cache_bucket_dir
            )
            Path(path_to_parent_dir).mkdir(parents=True, exist_ok=True)
            path_to_tmp_dir = tempfile.mkdtemp(
                prefix=".tmp-", dir=path_to_parent_dir
            )
            try:
                jinja_environment.compile_templates(
                    path_to_tmp_dir,
                    zip=None,
                    filter_func=filter_function_,
                    ignore_errors=False,
                )
                with open(
                    os.path.join(path_to_tmp_dir, self.COMPLETE_MARKER),
                    "w",
                    encoding="utf-8",
                ) as marker_file:
                    marker_file.write(fingerprint + "\n")
                try:
                    os.rename(
                        path_to_tmp_dir, self.path_to_jinja_cache_bucket_dir
                    )
                except OSError:
                    # Another StrictDoc process compiled the same bucket in
                    # the meantime. Use it if it is complete.
                    if not self.is_jinja_cache_complete(fingerprint):
                        raise
            finally:
                shutil.rmtree(path_to_tmp_dir, ignore_errors=True)

    def jinja_environment(self) -> JinjaEnvironment:
        if self._jinja_environment is not None:
            return self._jinja_environment
        self._jinja_environment = JinjaEnvironment(
            Environment(
                loader=ChoiceLoader(
                    [
                        ModuleLoader(self.path_to_jinja_cache_bucket_dir),
                        # A template that cannot be imported from the
                        # compiled cache (e.g., cache files deleted while the
                        # server runs) is compiled from its source instead of
                        # failing every page with TemplateNotFound.
                        FileSystemLoader(
                            environment.get_path_to_html_templates()
                        ),
                    ]
                ),
                undefined=StrictUndefined,
                extensions=[AssertExtension],
                autoescape=True,
            )
        )
        return self._jinja_environment

    def reset_jinja_environment_if_outdated(
        self, strictdoc_last_update: datetime.datetime
    ) -> None:
        assert isinstance(strictdoc_last_update, datetime.datetime)

        if os.path.isdir(self.path_to_jinja_cache_bucket_dir):
            jinja_cache_files: List[str] = list(
                glob.iglob(
                    f"{self.path_to_jinja_cache_bucket_dir}/**/*.py",
                    recursive=True,
                )
            )

            if len(jinja_cache_files) == 0:
                self._jinja_environment = None
                shutil.rmtree(self.path_to_jinja_cache_bucket_dir)
                return

            jinja_cache_mtime = get_file_modification_time(jinja_cache_files[0])

            if strictdoc_last_update > jinja_cache_mtime:
                self._jinja_environment = None
                shutil.rmtree(self.path_to_jinja_cache_bucket_dir)
