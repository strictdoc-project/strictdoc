# mypy: disable-error-code="attr-defined,no-untyped-call,no-untyped-def"
import datetime
import glob
import hashlib
import os.path
import shutil
from pathlib import Path
from typing import List, Optional

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


class JinjaEnvironment:
    environment: Environment

    def __init__(self, environment: Environment):
        self.environment = environment

    def get_template(self, *args, **kwargs) -> Template:
        return self.environment.get_template(*args, **kwargs)

    def render_template_as_markup(
        self, template: str, *args, **kwargs
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
    ):
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
    def __init__(self):
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
    def __init__(self, project_config: ProjectConfig):
        path_to_output_dir_hash = hashlib.md5(
            project_config.output_dir.encode("utf-8")
        ).hexdigest()
        self.path_to_jinja_cache_bucket_dir = os.path.join(
            project_config.get_path_to_cache_dir(),
            "jinja",
            path_to_output_dir_hash,
        )
        self._jinja_environment: Optional[JinjaEnvironment] = None

    def compile_jinja_templates(self):
        if os.path.isdir(self.path_to_jinja_cache_bucket_dir):
            return
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

            Path(self.path_to_jinja_cache_bucket_dir).mkdir(
                parents=True, exist_ok=True
            )
            jinja_environment.compile_templates(
                self.path_to_jinja_cache_bucket_dir,
                zip=None,
                filter_func=filter_function_,
                ignore_errors=False,
            )

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
                HTMLTemplates._jinja_environment = None
                shutil.rmtree(self.path_to_jinja_cache_bucket_dir)
