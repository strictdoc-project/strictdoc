"""
This script is a Python API example for StrictDoc that demonstrates a typical
user task of querying the contents of the SDoc trace index.

The task is as follows:

Given:

- High-level requirements (safety goals, SG).
- Lower-level requirements (RQ) linked to them as children.
- The lowest-level requirements (hardware requirements, HWR) linked to RQ as children.
- Each HWR has a "hardware module" attribute: SG <-- RQ <-- HWR [Module]

Task:

Collect all hardware modules for all requirements linked to a single SG.
"""

# Ignore StrictDoc linter warnings about print() statements in this example.
# All print statements in this script are intentionally used for demonstration purposes.
# ruff: noqa: T201

import os
import re
import sys

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.parallelizer import Parallelizer


def alphanumeric_sort_key(s: str):
    """
    Sorting key for alphanumeric sorting of elements.
    """

    return [int(part) if part.isdigit() else part
            for part in re.split(r"(\d+)", s)]


def main():
    cwd = os.getcwd()

    project_config = ProjectConfig(input_paths=[cwd])

    project_config.validate_and_finalize()

    parallelizer = Parallelizer.create(parallelize=True)
    try:
        traceability_index: TraceabilityIndex = (
            TraceabilityIndexBuilder.create(
                project_config=project_config,
                parallelizer=parallelizer,
            )
        )
    except DocumentTreeError as exc:
        print(exc.to_print_message())  # noqa: T201
        sys.exit(1)

    safety_goals_document = traceability_index.get_document_by_title(
        "Example: Safety goals"
    )

    map_safety_goals_to_modules: dict[SDocNode, set[str]] = {}

    document_iterator = traceability_index.get_document_iterator(safety_goals_document)
    for node_, _ in document_iterator.all_content():
        # Ignore non-requirement nodes in this document.
        if node_.node_type != "SAFETY_GOAL":
            continue

        # This trivial example does not use included documents but filter them
        # out here anyway for correctness.
        if not isinstance(node_, SDocNode):
            continue

        # assert_cast is needed to make the type checker happy.
        safety_goal: SDocNode = assert_cast(node_, SDocNode)

        safety_goal_child_requirements = traceability_index.get_children_requirements(safety_goal)

        for child_requirement_ in safety_goal_child_requirements:
            child_requirement_hardware_requirements = traceability_index.get_children_requirements(child_requirement_)
            for hardware_requirement_ in child_requirement_hardware_requirements:
                hardware_module_field = hardware_requirement_.get_field_by_name("MODULE")
                hardware_module = hardware_module_field.get_text_value()

                if safety_goal not in map_safety_goals_to_modules:
                    map_safety_goals_to_modules[safety_goal] = set()
                map_safety_goals_to_modules[safety_goal].add(hardware_module)

    print("Safety goals mapped to hardware modules:")
    for idx_, (safety_goal_, hardware_modules_) in enumerate(map_safety_goals_to_modules.items(), start=1):
        print(
            f"{idx_}) Safety goal: '{safety_goal_.reserved_title}'. "
            f"Hardware modules: {sorted(hardware_modules_, key=alphanumeric_sort_key)}"
        )

if __name__ == "__main__":
    main()
