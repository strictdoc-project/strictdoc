import ast
import datetime
import os
import shutil
import tempfile
from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Union

from strictdoc.core.project_config import (
    ProjectConfig,
    ProjectConfigDefault,
    ProjectConfigLoader,
    ProjectFeature,
)
from strictdoc.helpers.file_system import file_open_read_utf8

SettingValue = Union[int, List[str]]


@dataclass(frozen=True)
class ProjectSettingDefinition:
    name: str
    kind: str
    default_value: SettingValue


@dataclass(frozen=True)
class ProjectSettingState:
    definition: ProjectSettingDefinition
    value: SettingValue
    source: str
    editable: bool
    message: Optional[str]


@dataclass(frozen=True)
class ProjectSettingsInspection:
    config_path: str
    settings: List[ProjectSettingState]
    writable: bool
    message: Optional[str]


@dataclass(frozen=True)
class ProjectSettingsSaveResult:
    changed: bool
    saved_version_path: Optional[str]


PROJECT_SETTING_DEFINITIONS: List[ProjectSettingDefinition] = [
    ProjectSettingDefinition(
        name="project_features",
        kind="features",
        default_value=[
            feature_.value if isinstance(feature_, ProjectFeature) else feature_
            for feature_ in ProjectConfigDefault.DEFAULT_FEATURES
        ],
    ),
]


class ProjectSettingsManager:
    MAX_SAVED_VERSIONS = 5

    def __init__(self, project_config: ProjectConfig) -> None:
        self.project_config = project_config
        if project_config.config_path is not None:
            self.config_path = project_config.config_path
        else:
            project_root_path = project_config.get_project_root_path()
            if not os.path.isdir(project_root_path):
                project_root_path = os.path.dirname(project_root_path)
            self.config_path = os.path.join(
                project_root_path, "strictdoc_config.py"
            )

    def inspect(self) -> ProjectSettingsInspection:
        config_source = self._read_config_source()
        if config_source is None:
            return ProjectSettingsInspection(
                config_path=self.config_path,
                settings=self._states_for_missing_config(),
                writable=self._target_directory_is_writable(),
                message=None,
            )

        if not self.config_path.endswith(".py"):
            return ProjectSettingsInspection(
                config_path=self.config_path,
                settings=self._readonly_states(
                    "StrictDoc cannot edit this type of settings file."
                ),
                writable=False,
                message="Edit this settings file manually.",
            )

        project_config_call: Optional[ast.Call] = None
        extending_target: Optional[
            tuple[str, Dict[str, ast.expr], ast.Return]
        ] = None
        try:
            extending_target = self._find_extending_config_target(config_source)
        except ValueError:
            try:
                project_config_call = self._find_project_config_call(
                    config_source
                )
            except (SyntaxError, ValueError):
                pass
        except SyntaxError:
            pass

        if project_config_call is None and extending_target is None:
            message = (
                "StrictDoc cannot safely edit this settings file. "
                "Edit the file manually."
            )
            return ProjectSettingsInspection(
                config_path=self.config_path,
                settings=self._readonly_states(message),
                writable=False,
                message=message,
            )

        if project_config_call is not None:
            configured_nodes = {
                keyword_.arg: keyword_.value
                for keyword_ in project_config_call.keywords
                if keyword_.arg is not None
            }
        else:
            assert extending_target is not None
            configured_nodes = extending_target[1]
        settings: List[ProjectSettingState] = []
        for definition_ in PROJECT_SETTING_DEFINITIONS:
            configured_node = configured_nodes.get(definition_.name)
            if configured_node is None:
                settings.append(
                    self._create_setting_state(
                        definition=definition_,
                        value=getattr(self.project_config, definition_.name),
                        source="default",
                        editable=True,
                        message=None,
                    )
                )
                continue
            editable = self._node_is_supported_literal(configured_node) or (
                definition_.kind == "features"
                and self._node_is_all_features_call(configured_node)
            )
            configured_value: Optional[SettingValue] = None
            if editable:
                configured_value = (
                    ["ALL_FEATURES"]
                    if self._node_is_all_features_call(configured_node)
                    else ast.literal_eval(configured_node)
                )
            settings.append(
                self._create_setting_state(
                    definition=definition_,
                    value=configured_value,
                    source="configuration file",
                    editable=editable,
                    message=(
                        None
                        if editable
                        else "Edit this setting manually in the settings file."
                    ),
                )
            )

        writable = self._target_directory_is_writable()
        writable_message: Optional[str] = (
            None if writable else "The configuration is not writable."
        )
        if not writable:
            settings = [
                ProjectSettingState(
                    definition=state_.definition,
                    value=state_.value,
                    source=state_.source,
                    editable=False,
                    message=writable_message,
                )
                for state_ in settings
            ]
        return ProjectSettingsInspection(
            config_path=self.config_path,
            settings=settings,
            writable=writable,
            message=writable_message,
        )

    def save(
        self,
        values: Dict[str, SettingValue],
    ) -> ProjectSettingsSaveResult:
        inspection = self.inspect()
        if not inspection.writable:
            raise ValueError(inspection.message)

        editable_names = {
            state_.definition.name
            for state_ in inspection.settings
            if state_.editable
        }
        if set(values) != editable_names:
            raise ValueError("The submitted settings do not match the form.")

        normalized_values = self._validate_values(values)
        current_values = {
            state_.definition.name: state_.value
            for state_ in inspection.settings
            if state_.editable
        }
        values_changed = normalized_values != current_values
        if not values_changed:
            return ProjectSettingsSaveResult(
                changed=False, saved_version_path=None
            )

        source = self._read_config_source()
        if source is None:
            changed_values = {
                name_: value_
                for name_, value_ in normalized_values.items()
                if value_ != current_values[name_]
            }
            candidate_source = self._create_config_source(changed_values)
        else:
            changed_values = {
                name_: value_
                for name_, value_ in normalized_values.items()
                if value_ != current_values[name_]
            }
            try:
                extending_target = self._find_extending_config_target(source)
            except ValueError:
                extending_target = None
            if extending_target is None:
                project_config_call = self._find_project_config_call(source)
                candidate_source = self._replace_values(
                    source=source,
                    project_config_call=project_config_call,
                    values=changed_values,
                )
            else:
                returned_name, assignments, return_node = extending_target
                candidate_source = self._replace_assignment_values(
                    source=source,
                    returned_name=returned_name,
                    assignments=assignments,
                    return_node=return_node,
                    values=changed_values,
                )

        self._validate_candidate(candidate_source)
        saved_version_path = self._save_candidate(candidate_source)
        return ProjectSettingsSaveResult(
            changed=True,
            saved_version_path=saved_version_path,
        )

    @staticmethod
    def default_values() -> Dict[str, SettingValue]:
        return {
            definition_.name: definition_.default_value
            for definition_ in PROJECT_SETTING_DEFINITIONS
        }

    @staticmethod
    def stage_inspection(
        inspection: ProjectSettingsInspection,
        values: Dict[str, SettingValue],
    ) -> ProjectSettingsInspection:
        staged_settings: List[ProjectSettingState] = []
        for setting_state_ in inspection.settings:
            setting_name = setting_state_.definition.name
            if not setting_state_.editable or setting_name not in values:
                staged_settings.append(setting_state_)
                continue
            staged_settings.append(
                replace(
                    setting_state_,
                    value=values[setting_name],
                    source="configuration file",
                )
            )
        return replace(inspection, settings=staged_settings)

    def _create_setting_state(
        self,
        *,
        definition: ProjectSettingDefinition,
        value: Optional[SettingValue],
        source: str,
        editable: bool,
        message: Optional[str],
    ) -> ProjectSettingState:
        if value is None:
            value = getattr(self.project_config, definition.name)
        if definition.kind == "features":
            assert isinstance(value, list)
            value = [
                feature_.value
                if isinstance(feature_, ProjectFeature)
                else feature_
                for feature_ in value
            ]
        return ProjectSettingState(
            definition=definition,
            value=value,
            source=source,
            editable=editable,
            message=message,
        )

    def _states_for_missing_config(self) -> List[ProjectSettingState]:
        return [
            self._create_setting_state(
                definition=definition_,
                value=definition_.default_value,
                source="default",
                editable=True,
                message=None,
            )
            for definition_ in PROJECT_SETTING_DEFINITIONS
        ]

    def _readonly_states(self, message: str) -> List[ProjectSettingState]:
        return [
            self._create_setting_state(
                definition=definition_,
                value=None,
                source="configuration file",
                editable=False,
                message=message,
            )
            for definition_ in PROJECT_SETTING_DEFINITIONS
        ]

    def _read_config_source(self) -> Optional[str]:
        if not os.path.isfile(self.config_path):
            return None
        with file_open_read_utf8(self.config_path) as config_file:
            return config_file.read()

    def _target_directory_is_writable(self) -> bool:
        target_directory = os.path.dirname(self.config_path)
        return os.access(target_directory, os.W_OK)

    @staticmethod
    def _find_project_config_call(source: str) -> ast.Call:
        module = ast.parse(source)
        calls = [
            node_
            for node_ in ast.walk(module)
            if isinstance(node_, ast.Call)
            and (
                isinstance(node_.func, ast.Name)
                and node_.func.id == "ProjectConfig"
                or isinstance(node_.func, ast.Attribute)
                and node_.func.attr == "ProjectConfig"
            )
        ]
        if len(calls) != 1:
            raise ValueError(
                "The file must contain exactly one ProjectConfig(...) call."
            )
        return calls[0]

    @staticmethod
    def _find_extending_config_target(
        source: str,
    ) -> tuple[str, Dict[str, ast.expr], ast.Return]:
        module = ast.parse(source)
        create_config_functions = [
            node_
            for node_ in module.body
            if isinstance(node_, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node_.name == "create_config"
        ]
        if len(create_config_functions) != 1:
            raise ValueError("The configuration factory is ambiguous.")
        function = create_config_functions[0]
        return_nodes = [
            node_
            for node_ in ast.walk(function)
            if isinstance(node_, ast.Return)
        ]
        if len(return_nodes) != 1 or not isinstance(
            return_nodes[0].value, ast.Name
        ):
            raise ValueError("The configuration result is ambiguous.")
        return_node = return_nodes[0]
        returned_value = return_node.value
        assert isinstance(returned_value, ast.Name)
        returned_name = returned_value.id
        assignments: Dict[str, ast.expr] = {}
        for node_ in ast.walk(function):
            if not isinstance(node_, (ast.Assign, ast.AnnAssign)):
                continue
            targets = (
                node_.targets
                if isinstance(node_, ast.Assign)
                else [node_.target]
            )
            for target_ in targets:
                if (
                    isinstance(target_, ast.Attribute)
                    and isinstance(target_.value, ast.Name)
                    and target_.value.id == returned_name
                    and target_.attr == "project_features"
                ):
                    assignment_value = node_.value
                    if assignment_value is not None:
                        assignments[target_.attr] = assignment_value
        return returned_name, assignments, return_node

    @staticmethod
    def _node_is_all_features_call(node: ast.AST) -> bool:
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "all"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "ProjectFeature"
            and len(node.args) == 0
            and len(node.keywords) == 0
        )

    @staticmethod
    def _node_is_supported_literal(node: ast.AST) -> bool:
        try:
            value = ast.literal_eval(node)
        except (ValueError, TypeError):
            return False
        return isinstance(value, list) and all(
            isinstance(item_, str) for item_ in value
        )

    @staticmethod
    def _validate_values(
        values: Dict[str, SettingValue],
    ) -> Dict[str, SettingValue]:
        definitions_by_name = {
            definition_.name: definition_
            for definition_ in PROJECT_SETTING_DEFINITIONS
        }
        normalized: Dict[str, SettingValue] = {}
        for name_, value_ in values.items():
            definition = definitions_by_name[name_]
            if definition.kind == "features":
                if not isinstance(value_, list) or not all(
                    isinstance(feature_, str) for feature_ in value_
                ):
                    raise ValueError(f"{name_} must be a list of features.")
                unknown_features = set(value_) - set(ProjectFeature.all())
                if len(unknown_features) > 0:
                    raise ValueError(
                        f"Unknown project features: {sorted(unknown_features)}."
                    )
            normalized[name_] = value_
        return normalized

    @staticmethod
    def _create_config_source(values: Dict[str, SettingValue]) -> str:
        arguments = "\n".join(
            f"        {name_}={value_!r}," for name_, value_ in values.items()
        )
        return (
            "from strictdoc.core.project_config import ProjectConfig\n\n\n"
            "def create_config() -> ProjectConfig:\n"
            "    return ProjectConfig(\n"
            f"{arguments}\n"
            "    )\n"
        )

    @staticmethod
    def _replace_values(
        *,
        source: str,
        project_config_call: ast.Call,
        values: Dict[str, SettingValue],
    ) -> str:
        replacements: List[tuple[int, int, str]] = []
        existing_keywords = {
            keyword_.arg: keyword_
            for keyword_ in project_config_call.keywords
            if keyword_.arg is not None
        }
        line_offsets = [0]
        for line_ in source.splitlines(keepends=True):
            line_offsets.append(line_offsets[-1] + len(line_))

        missing_values: Dict[str, SettingValue] = {}
        for name_, value_ in values.items():
            keyword = existing_keywords.get(name_)
            if keyword is None:
                missing_values[name_] = value_
                continue
            value_node = keyword.value
            if name_ == "project_features" and isinstance(value_node, ast.List):
                replacements.extend(
                    ProjectSettingsManager._feature_list_replacements(
                        source=source,
                        list_node=value_node,
                        features=value_,
                        line_offsets=line_offsets,
                    )
                )
                continue
            assert value_node.end_lineno is not None
            assert value_node.end_col_offset is not None
            start = line_offsets[value_node.lineno - 1] + value_node.col_offset
            end = (
                line_offsets[value_node.end_lineno - 1]
                + value_node.end_col_offset
            )
            replacements.append((start, end, repr(value_)))

        if len(missing_values) > 0:
            assert project_config_call.end_lineno is not None
            assert project_config_call.end_col_offset is not None
            if project_config_call.lineno == project_config_call.end_lineno:
                closing_parenthesis = (
                    line_offsets[project_config_call.end_lineno - 1]
                    + project_config_call.end_col_offset
                    - 1
                )
                separator = (
                    ", " if len(project_config_call.keywords) > 0 else ""
                )
                insertion = separator + ", ".join(
                    f"{name_}={value_!r}"
                    for name_, value_ in missing_values.items()
                )
            else:
                closing_parenthesis = line_offsets[
                    project_config_call.end_lineno - 1
                ]
                closing_line = source.splitlines()[
                    project_config_call.end_lineno - 1
                ]
                closing_indent = len(closing_line) - len(
                    closing_line.lstrip(" ")
                )
                indent = " " * (closing_indent + 4)
                insertion = "".join(
                    f"{indent}{name_}={value_!r},\n"
                    for name_, value_ in missing_values.items()
                )
            replacements.append(
                (closing_parenthesis, closing_parenthesis, insertion)
            )

        candidate = source
        for start_, end_, replacement_ in sorted(replacements, reverse=True):
            candidate = candidate[:start_] + replacement_ + candidate[end_:]
        return candidate

    @staticmethod
    def _replace_assignment_values(
        *,
        source: str,
        returned_name: str,
        assignments: Dict[str, ast.expr],
        return_node: ast.Return,
        values: Dict[str, SettingValue],
    ) -> str:
        line_offsets = [0]
        for line_ in source.splitlines(keepends=True):
            line_offsets.append(line_offsets[-1] + len(line_))

        replacements: List[tuple[int, int, str]] = []
        missing_values: Dict[str, SettingValue] = {}
        for name_, value_ in values.items():
            value_node = assignments.get(name_)
            if value_node is None:
                missing_values[name_] = value_
                continue
            assert value_node.end_lineno is not None
            assert value_node.end_col_offset is not None
            start = line_offsets[value_node.lineno - 1] + value_node.col_offset
            end = (
                line_offsets[value_node.end_lineno - 1]
                + value_node.end_col_offset
            )
            replacements.append((start, end, repr(value_)))

        if len(missing_values) > 0:
            insertion_point = line_offsets[return_node.lineno - 1]
            indentation = " " * return_node.col_offset
            insertion = "".join(
                f"{indentation}{returned_name}.{name_} = {value_!r}\n"
                for name_, value_ in missing_values.items()
            )
            replacements.append((insertion_point, insertion_point, insertion))

        candidate = source
        for start_, end_, replacement_ in sorted(replacements, reverse=True):
            candidate = candidate[:start_] + replacement_ + candidate[end_:]
        return candidate

    @staticmethod
    def _feature_list_replacements(
        *,
        source: str,
        list_node: ast.List,
        features: SettingValue,
        line_offsets: List[int],
    ) -> List[tuple[int, int, str]]:
        assert isinstance(features, list)
        string_elements = [
            element_
            for element_ in list_node.elts
            if isinstance(element_, ast.Constant)
            and isinstance(element_.value, str)
        ]
        if len(string_elements) != len(list_node.elts):
            raise ValueError(
                "Project features must contain only literal feature names."
            )
        assert list_node.end_lineno is not None
        assert list_node.end_col_offset is not None
        if list_node.lineno == list_node.end_lineno:
            start = line_offsets[list_node.lineno - 1] + list_node.col_offset
            end = (
                line_offsets[list_node.end_lineno - 1]
                + list_node.end_col_offset
            )
            return [(start, end, repr(features))]

        replacements: List[tuple[int, int, str]] = []
        existing_features = {element_.value for element_ in string_elements}
        requested_features = set(features)
        source_lines = source.splitlines(keepends=True)
        for element_ in string_elements:
            if element_.value in requested_features:
                continue
            assert element_.end_lineno is not None
            assert element_.end_col_offset is not None
            line_start = line_offsets[element_.lineno - 1]
            line_end = line_offsets[element_.end_lineno]
            line = source_lines[element_.lineno - 1]
            comment_position = line.find("#", element_.end_col_offset)
            replacement = ""
            if comment_position >= 0:
                replacement = (
                    " " * element_.col_offset + line[comment_position:]
                )
            replacements.append((line_start, line_end, replacement))

        missing_features = [
            feature_
            for feature_ in features
            if feature_ not in existing_features
        ]
        if len(missing_features) > 0:
            insertion_point = line_offsets[list_node.end_lineno - 1]
            element_indent = (
                string_elements[0].col_offset
                if len(string_elements) > 0
                else list_node.col_offset + 4
            )
            insertion = "".join(
                f"{' ' * element_indent}{feature_!r},\n"
                for feature_ in missing_features
            )
            replacements.append((insertion_point, insertion_point, insertion))
        return replacements

    def _validate_candidate(self, candidate_source: str) -> None:
        ast.parse(candidate_source)
        target_directory = os.path.dirname(self.config_path)
        temporary_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf8",
                suffix=".py",
                dir=target_directory,
                delete=False,
            ) as temporary_file:
                temporary_file.write(candidate_source)
                temporary_path = temporary_file.name
            candidate_config = ProjectConfigLoader.load_from_python(
                config_py_path=temporary_path
            )
            candidate_config.input_paths = self.project_config.input_paths
            candidate_config.source_root_path = (
                self.project_config.source_root_path
            )
            candidate_config.validate_and_finalize()
        finally:
            if temporary_path is not None and os.path.exists(temporary_path):
                os.unlink(temporary_path)

    def _save_candidate(self, candidate_source: str) -> Optional[str]:
        saved_version_path: Optional[str] = None
        if os.path.isfile(self.config_path):
            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y%m%dT%H%M%S%fZ"
            )
            saved_version_path = f"{self.config_path}.saved.{timestamp}"
            shutil.copy2(self.config_path, saved_version_path)

        target_directory = os.path.dirname(self.config_path)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf8",
            dir=target_directory,
            delete=False,
        ) as temporary_file:
            temporary_file.write(candidate_source)
            temporary_path = temporary_file.name
        if os.path.isfile(self.config_path):
            existing_mode = os.stat(self.config_path).st_mode
            os.chmod(temporary_path, existing_mode)
        try:
            os.replace(temporary_path, self.config_path)
        finally:
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)

        self._rotate_saved_versions()
        return saved_version_path

    def _rotate_saved_versions(self) -> None:
        target_directory = os.path.dirname(self.config_path)
        prefix = f"{os.path.basename(self.config_path)}.saved."
        versions = sorted(
            (
                os.path.join(target_directory, filename_)
                for filename_ in os.listdir(target_directory)
                if filename_.startswith(prefix)
            ),
            reverse=True,
        )
        for old_version_ in versions[self.MAX_SAVED_VERSIONS :]:
            try:
                os.unlink(old_version_)
            except OSError:
                pass
