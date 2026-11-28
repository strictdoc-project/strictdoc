import datetime
import glob
import hashlib
import os.path
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from jinja2 import (
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

# The size of the cache of loaded templates in each Jinja environment. -1
# means no limit: Jinja then uses a plain dict.
#
# The default cache is an LRU cache of 400 templates. Every cache hit moves
# the template to the end of a deque with deque.remove(), which scans all
# loaded templates. Every {% include %} is a cache hit, and a document page
# runs thousands of includes. StrictDoc has about 300 templates, so the LRU
# cache never evicts a template, and the reordering is wasted work. Without
# the limit, the export of the StrictDoc documentation is about 6% faster.
JINJA_TEMPLATE_CACHE_SIZE = -1


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


# The HTMLTemplates object of each kind of templates in this process, by
# key. See HTMLTemplates for how worker processes use it.
_html_templates_of_this_process: Dict[str, "HTMLTemplates"] = {}

_NORMAL_HTML_TEMPLATES_KEY = "normal"


class HTMLTemplates:
    """
    The Jinja templates of the HTML export.

    An HTMLTemplates object can be sent to a worker process, for example in
    a task of the parallelizer. A Jinja environment cannot be pickled, and
    loading the templates again for every task would be slow. As a result,
    an HTMLTemplates object is pickled as a reference: the kind of the
    templates and, for compiled templates, their cache folder. Unpickling
    the reference returns the HTMLTemplates object of the same kind in the
    receiving process:

    - In the main process and in a forked worker process, this is the
      object that the main process created last for these templates. Each
      HTMLTemplates object registers itself when it is created.
    - In a worker process that is not forked (spawn, for example on
      Windows), the first task creates the object, and later tasks reuse
      it. Compiled templates are read from the cache folder that the main
      process has filled.
    """

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
                cache_size=JINJA_TEMPLATE_CACHE_SIZE,
            )
        )
        _html_templates_of_this_process[_NORMAL_HTML_TEMPLATES_KEY] = self

    def __reduce__(self) -> Tuple[Callable[[], HTMLTemplates], Tuple[()]]:
        return _get_normal_html_templates_of_this_process, ()

    def jinja_environment(self) -> JinjaEnvironment:
        return self._jinja_environment


def _get_normal_html_templates_of_this_process() -> HTMLTemplates:
    html_templates = _html_templates_of_this_process.get(
        _NORMAL_HTML_TEMPLATES_KEY
    )
    if html_templates is not None:
        return html_templates
    return NormalHTMLTemplates()


class CompiledHTMLTemplates(HTMLTemplates):
    def __init__(self, project_config: ProjectConfig):
        path_to_output_dir_hash = hashlib.md5(
            project_config.output_dir.encode("utf-8")
        ).hexdigest()
        self._initialize(
            os.path.join(
                project_config.get_path_to_cache_dir(),
                "jinja",
                path_to_output_dir_hash,
            )
        )

    def _initialize(self, path_to_jinja_cache_bucket_dir: str) -> None:
        self.path_to_jinja_cache_bucket_dir: str = (
            path_to_jinja_cache_bucket_dir
        )
        self._jinja_environment: Optional[JinjaEnvironment] = None
        _html_templates_of_this_process[
            _get_compiled_html_templates_key(path_to_jinja_cache_bucket_dir)
        ] = self

    def __reduce__(self) -> Tuple[Callable[[str], HTMLTemplates], Tuple[str]]:
        return (
            _get_compiled_html_templates_of_this_process,
            (self.path_to_jinja_cache_bucket_dir,),
        )

    def compile_jinja_templates(self) -> None:
        if os.path.isdir(self.path_to_jinja_cache_bucket_dir):
            return
        jinja_environment = Environment(
            loader=FileSystemLoader(environment.get_path_to_html_templates()),
            undefined=StrictUndefined,
            extensions=[AssertExtension],
            autoescape=True,
            cache_size=JINJA_TEMPLATE_CACHE_SIZE,
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

            # Compile into a temporary folder and rename it into place, so a
            # run that stops mid-compile cannot leave a half-filled bucket.
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
                try:
                    os.rename(
                        path_to_tmp_dir, self.path_to_jinja_cache_bucket_dir
                    )
                except OSError:
                    # Another process created the bucket first. Use it.
                    if not os.path.isdir(self.path_to_jinja_cache_bucket_dir):
                        raise
            finally:
                shutil.rmtree(path_to_tmp_dir, ignore_errors=True)

    def jinja_environment(self) -> JinjaEnvironment:
        if self._jinja_environment is not None:
            return self._jinja_environment
        assert os.path.isdir(self.path_to_jinja_cache_bucket_dir)
        self._jinja_environment = JinjaEnvironment(
            Environment(
                loader=ModuleLoader(self.path_to_jinja_cache_bucket_dir),
                undefined=StrictUndefined,
                extensions=[AssertExtension],
                autoescape=True,
                cache_size=JINJA_TEMPLATE_CACHE_SIZE,
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

            jinja_cache_mtime = get_file_modification_time(jinja_cache_files[0])

            if strictdoc_last_update > jinja_cache_mtime:
                self._jinja_environment = None
                shutil.rmtree(self.path_to_jinja_cache_bucket_dir)


def _get_compiled_html_templates_key(
    path_to_jinja_cache_bucket_dir: str,
) -> str:
    return f"compiled:{path_to_jinja_cache_bucket_dir}"


def _get_compiled_html_templates_of_this_process(
    path_to_jinja_cache_bucket_dir: str,
) -> HTMLTemplates:
    html_templates = _html_templates_of_this_process.get(
        _get_compiled_html_templates_key(path_to_jinja_cache_bucket_dir)
    )
    if html_templates is not None:
        return html_templates
    # Without a ProjectConfig: the cache folder is all that the compiled
    # templates need in a worker process.
    compiled_html_templates = CompiledHTMLTemplates.__new__(
        CompiledHTMLTemplates
    )
    compiled_html_templates._initialize(path_to_jinja_cache_bucket_dir)  # noqa: SLF001
    return compiled_html_templates
