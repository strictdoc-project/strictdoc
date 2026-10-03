"""
Mutation check of the specification graph unit tests.

Run from the repository root, in the environment of the check dependency
group (uv run --group check):
    python -m developer.examples.specification_graph.mutations

To run selected mutations, add their identifiers, for example: S5 R4.

Each mutation breaks one rule of the graph generator in one source file. The
script applies one mutation at a time, runs the unit tests of the generator,
and restores the file. The "Fails if" lines in the test docstrings describe
these mutations.

The script exits with a non-zero code if a mutation fails no test, if a test
fails under no mutation, or if a mutation does not find its code.
"""

import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

PACKAGE_PATH = "strictdoc/features/specification_graph/svg_graph/"
TESTS_PATH = "tests/unit/strictdoc/features/specification_graph"
NORMALIZATION = PACKAGE_PATH + "normalization.py"
STRUCTURE = PACKAGE_PATH + "levels_structure.py"
ROUTING = PACKAGE_PATH + "levels_routing.py"
GEOMETRY = PACKAGE_PATH + "levels_geometry.py"
SERIALIZER = PACKAGE_PATH + "svg_serializer.py"
STRUCTURE_LAYOUT = PACKAGE_PATH + "structure_layout.py"
LANES = PACKAGE_PATH + "lane_assignment.py"
GATES = PACKAGE_PATH + "gate_ports.py"
STRUCTURE_GEOMETRY = PACKAGE_PATH + "structure_geometry.py"
STRUCTURE_ROUTING = PACKAGE_PATH + "structure_routing.py"
STRUCTURE_STRETCHES = PACKAGE_PATH + "structure_stretches.py"


@dataclass(frozen=True)
class Mutation:
    identifier: str
    description: str
    path: str
    # The original code. The code must occur exactly once in the file.
    original: str
    replacement: str
    # Code to append to the mutated file.
    appendix: str = ""


# A recursive version of the cycle search. It hits the recursion limit on a
# deep graph.
RECURSIVE_CYCLE_SEARCH = """

def _strongly_connected_components(nodes, edges):
    successors = {node_.node_id: [] for node_ in nodes}
    for edge_ in edges:
        successors[edge_.source_id].append(edge_.target_id)
    index, low, stack, on_stack, result = {}, {}, [], set(), []

    def visit(node_id):
        index[node_id] = low[node_id] = len(index)
        stack.append(node_id)
        on_stack.add(node_id)
        for successor_id in successors[node_id]:
            if successor_id not in index:
                visit(successor_id)
                low[node_id] = min(low[node_id], low[successor_id])
            elif successor_id in on_stack:
                low[node_id] = min(low[node_id], index[successor_id])
        if low[node_id] == index[node_id]:
            component = []
            while True:
                member_id = stack.pop()
                on_stack.discard(member_id)
                component.append(member_id)
                if member_id == node_id:
                    break
            result.append(component)

    for node_ in nodes:
        if node_.node_id not in index:
            visit(node_.node_id)
    return result
"""

MUTATIONS = (
    Mutation(
        "N1",
        "children pushed in input order",
        NORMALIZATION,
        "(child_, node.node_id) for child_ in reversed(node.children)",
        "(child_, node.node_id) for child_ in node.children",
    ),
    Mutation(
        "N2",
        "no duplicate node check",
        NORMALIZATION,
        "if node.node_id in parent_ids:",
        "if False:",
    ),
    Mutation(
        "N3",
        "no unknown endpoint check",
        NORMALIZATION,
        "if endpoint_id_ not in node_index:",
        "if False:",
    ),
    Mutation(
        "N4",
        "children accepted in any mode",
        NORMALIZATION,
        "if len(node.children) > 0 and graph.mode is not LayoutMode.STRUCTURE:",
        "if False:",
    ),
    Mutation(
        "N5",
        "node group accepted in any mode",
        NORMALIZATION,
        "and graph.mode is not LayoutMode.LEVELS_WITH_GROUPS\n        ):",
        "and False\n        ):",
    ),
    Mutation(
        "N6",
        "no unknown group check",
        NORMALIZATION,
        "if node_.group_id is not None and node_.group_id not in group_ids:",
        "if False:",
    ),
    Mutation(
        "N7",
        "exact duplicates kept",
        NORMALIZATION,
        "if edge_ in seen:",
        "if False:",
    ),
    Mutation(
        "N8",
        "self-loops kept",
        NORMALIZATION,
        "if edge_.source_id == edge_.target_id:",
        "if False:",
    ),
    Mutation(
        "N9",
        "edge numbering starts at 0",
        NORMALIZATION,
        'edge_id=f"edge-{index_ + 1}"',
        'edge_id=f"edge-{index_}"',
    ),
    Mutation(
        "N10",
        "cycles numbered backwards",
        NORMALIZATION,
        "key=lambda component_: node_index[component_[0]],",
        "key=lambda component_: -node_index[component_[0]],",
    ),
    Mutation(
        "N11",
        "edge that closes a cycle takes part in the levels",
        NORMALIZATION,
        "closes_cycle_ = _reaches(",
        "closes_cycle_ = False and _reaches(",
    ),
    Mutation(
        "N12",
        "ancestor link detected in one direction only",
        NORMALIZATION,
        "return _is_ancestor(source_id, target_id, parent_ids) or _is_ancestor("
        "\n        target_id, source_id, parent_ids\n    )",
        "return _is_ancestor(source_id, target_id, parent_ids)",
    ),
    Mutation(
        "T1",
        "recursive cycle search",
        NORMALIZATION,
        "def _strongly_connected_components(\n",
        "def _strongly_connected_components_iterative(\n",
        appendix=RECURSIVE_CYCLE_SEARCH,
    ),
    Mutation(
        "S1",
        "node stands below its shallowest parent",
        STRUCTURE,
        "level_of[node_id_] = 1 + max(",
        "level_of[node_id_] = 1 + min(",
    ),
    Mutation(
        "S2",
        "no root correction",
        STRUCTURE,
        "reference_level_ is not None\n"
        "                    and reference_level_ > root_level[root_id_]",
        "False",
    ),
    Mutation(
        "S3",
        "root correction picks the farthest child",
        STRUCTURE,
        "or candidate_ < reference_level_",
        "or candidate_ > reference_level_",
    ),
    Mutation(
        "S4",
        "corrected root takes the column of the middle child",
        STRUCTURE,
        "target_column_ = child_columns_[(len(child_columns_) - 1) // 2] + 1",
        "target_column_ = child_columns_[(len(child_columns_) - 1) // 2]",
    ),
    Mutation(
        "S5",
        "losing node stands right of the winner",
        STRUCTURE,
        "selected_ = self.column_of[last_contender_of[winner_id_]] + 1",
        "selected_ = self.column_of[winner_id_] + 1",
    ),
    Mutation(
        "S6",
        "islands overlap",
        STRUCTURE,
        "next_column += island_layout_.column_count",
        "next_column += 0",
    ),
    Mutation(
        "S7",
        "standalone grid always square",
        STRUCTURE,
        "next_column\n"
        "            if next_column > 0\n"
        "            else _square_grid_width(len(standalone_node_ids))",
        "_square_grid_width(len(standalone_node_ids))",
    ),
    Mutation(
        "S8",
        "standalone grid is one row",
        STRUCTURE,
        "    return width if width * width == node_count else width + 1",
        "    return node_count",
    ),
    Mutation(
        "S9",
        "any mode accepted",
        STRUCTURE,
        "if normalized_graph.mode is not LayoutMode.LEVELS:",
        "if False:",
    ),
    Mutation(
        "S10",
        "only upward edges across levels are skip edges",
        STRUCTURE,
        "positions[edge_.target_id].row != 1",
        "positions[edge_.target_id].row > 1",
    ),
    Mutation(
        "S11",
        "node stands on the level of its parent",
        STRUCTURE,
        "level_of[node_id_] = 1 + max(",
        "level_of[node_id_] = 0 + max(",
    ),
    Mutation(
        "R1",
        "no straight edges",
        ROUTING,
        "and gate_ not in straight_gates",
        "and False",
    ),
    Mutation(
        "R2",
        "lane priority inverted",
        LANES,
        "prefer_entry = priority is LaneConflictPriority.ENTRY",
        "prefer_entry = priority is not LaneConflictPriority.ENTRY",
    ),
    Mutation(
        "R3",
        "near target uses the channel near the source",
        ROUTING,
        "    if options.skip_channel_choice is SkipChannelChoice.NEAR_SOURCE:",
        "    if True:",
    ),
    Mutation(
        "R4",
        "unsafe groups numbered per face",
        GATES,
        "    if len(upper) == 0 or len(lower) == 0:\n        return False",
        "    if True:\n        return False",
    ),
    Mutation(
        "R5",
        "safe groups share one list",
        GATES,
        "    if len(upper) == 0 or len(lower) == 0:\n        return False",
        "    if len(upper) == 0 or len(lower) == 0:\n"
        "        return False\n"
        "    return True",
    ),
    Mutation(
        "R6",
        "shared list interleaves the faces",
        GATES,
        "numbered_lists_ = [upper_ + lower_]",
        "numbered_lists_ = [sorted(upper_ + lower_, "
        "key=lambda e_: e_.sort_key, reverse=side_ == -1)]",
    ),
    Mutation(
        "R7",
        "left side ports not ordered from the center outward",
        GATES,
        "            upper_.reverse()\n            lower_.reverse()",
        "            pass",
    ),
    Mutation(
        "R8",
        "overlapping segments may share a lane",
        LANES,
        "            while any(\n                lanes[placed_key_] == lane_",
        "            while False and any(\n"
        "                lanes[placed_key_] == lane_",
    ),
    Mutation(
        "R9",
        "halves of the right-hand traffic swapped",
        ROUTING,
        "half=0 if goes_left_ else 1,\n                    members=(",
        "half=1 if goes_left_ else 0,\n                    members=(",
    ),
    Mutation(
        "G1",
        "gate center does not shift",
        GEOMETRY,
        "    if left_needed > half_width:",
        "    if False:",
    ),
    Mutation(
        "G2",
        "column does not widen",
        GEOMETRY,
        "widths[column_] = max(widths[column_], grid_ceil(needed_, config))",
        "widths[column_] = widths[column_]",
    ),
    Mutation(
        "G3",
        "pitch comes from the longest list of the gate side",
        GEOMETRY,
        "port.list_size, gate_layout.side_widths[side], config",
        "list_sizes_by_gate[_gate_of(port, structure)][side],"
        " gate_layout.side_widths[side], config",
    ),
    Mutation(
        "G4",
        "outermost port ignores the port margin",
        GEOMETRY,
        "    half_width = node_width / 2 - config.port_margin",
        "    half_width = node_width / 2",
    ),
    Mutation(
        "G5",
        "horizontal channel ignores the lane clearance",
        GEOMETRY,
        "(lane_count - 1) * config.lane_pitch + 2 * config.lane_clearance,",
        "(lane_count + 1) * config.lane_pitch,",
    ),
    Mutation(
        "L1",
        "composite node does not break the column of simple nodes",
        STRUCTURE_LAYOUT,
        "        if len(child_.children) == 0:",
        "        if True:",
    ),
    Mutation(
        "L2",
        "relation inside a root child connects the child",
        STRUCTURE_LAYOUT,
        "        if source_root_ != target_root_:",
        "        if True:",
    ),
    Mutation(
        "L3",
        "block uses the square rule while a connected row exists",
        STRUCTURE_GEOMETRY,
        "            row_width\n            if len(row_columns) > 0\n",
        "            row_width\n            if False\n",
    ),
    Mutation(
        "L4",
        "block picks the width farthest from a square",
        STRUCTURE_GEOMETRY,
        "        if score_ < best_score:",
        "        if best_width == 0.0 or score_ > best_score:",
    ),
    Mutation(
        "L7",
        "block box takes the leftmost place instead of the highest",
        STRUCTURE_GEOMETRY,
        "if best_ is None or (top_, left_) < (best_[1], best_[0]):",
        "if best_ is None:",
    ),
    Mutation(
        "R10",
        "port order not mirrored for a downward relation",
        GATES,
        "    if endpoint.flows_down:\n        return (-position, -secondary), index",
        "    if False:\n        return (-position, -secondary), index",
    ),
    Mutation(
        "SR1",
        "structure path cost compares the length before the bends",
        STRUCTURE_ROUTING,
        "cost_ = (bends_, length_, face_rank_)",
        "cost_ = (0, length_, face_rank_)",
    ),
    Mutation(
        "SR2",
        "no straight relation in the structure mode",
        STRUCTURE_ROUTING,
        "            if gate_ not in straight_gates:",
        "            if False:",
    ),
    Mutation(
        "SR4",
        "halves swapped in the horizontal channels of the structure mode",
        STRUCTURE_ROUTING,
        "half=0 if exit_ < entry_ else 1,",
        "half=1 if exit_ < entry_ else 0,",
    ),
    Mutation(
        "SR5",
        "halves swapped in the vertical channels of the structure mode",
        STRUCTURE_ROUTING,
        "half=1 if exit_y_ < entry_y_ else 0,",
        "half=0 if exit_y_ < entry_y_ else 1,",
    ),
    Mutation(
        "L5",
        "container height ignores the header",
        STRUCTURE_GEOMETRY,
        "self.config.container_header_height + area_height,",
        "area_height,",
    ),
    Mutation(
        "L6",
        "bottom corridor below the shortest column",
        STRUCTURE_GEOMETRY,
        "+ max(column_height_ for _, column_height_ in column_sizes)",
        "+ min(column_height_ for _, column_height_ in column_sizes)",
    ),
    Mutation(
        "BC1",
        "bottom corridor segment below the tallest column",
        STRUCTURE_GEOMETRY,
        "if low < right_ and high > left_",
        "if True",
    ),
    Mutation(
        "BC2",
        "corridor segment ignores the lane order",
        STRUCTURE_GEOMETRY,
        "y_ = max(y_, placed_y_ + config.lane_pitch)",
        "pass",
    ),
    Mutation(
        "BC3",
        "bottom corridor size ignores its segments",
        STRUCTURE_GEOMETRY,
        "(y_ + config.lane_clearance - tallest for _, _, y_ in placed),",
        "(0 for _, _, y_ in placed),",
    ),
    Mutation(
        "BC4",
        "path cost takes the bottom corridor below the tallest column",
        STRUCTURE_ROUTING,
        "            min(first_x, second_x),\n            max(first_x, second_x),",
        "            0.0,\n            0.0,",
    ),
    Mutation(
        "TP1",
        "through pass counts as a bend",
        STRUCTURE_ROUTING,
        "                            item.bends,\n                            length_,",
        "                            item.bends + 1,\n                            length_,",
    ),
    Mutation(
        "TP2",
        "segment under the columns ignores the height of its through pass",
        STRUCTURE_GEOMETRY,
        "through_y_ if through_y_ is not None else lowest_y_",
        "lowest_y_",
    ),
    Mutation(
        "RW1",
        "segments under the columns may lie closer than one lane pitch",
        STRUCTURE_GEOMETRY,
        "and abs(placed_y_ - y) < lane_pitch",
        "and False",
    ),
    Mutation(
        "RW2",
        "lane order applies across the rows under the columns",
        STRUCTURE_GEOMETRY,
        "            if not is_row_:\n"
        "                for placed_low_, placed_high_, placed_y_ in corridor_placed:",
        "            if True:\n"
        "                for placed_low_, placed_high_, placed_y_ in placed:",
    ),
    Mutation(
        "RW3",
        "segments under the columns meet by height, not by lane order",
        STRUCTURE_GEOMETRY,
        "bases, key=lambda base_: (base_[0].lane, base_[0].key)",
        "bases, key=lambda base_: (not base_[4], base_[3], base_[0].lane)",
    ),
    Mutation(
        "ST1",
        "shared stretches of two or more channels are not ordered",
        STRUCTURE_STRETCHES,
        "    if length < 2:\n        return None\n",
        "    if True:\n        return None\n",
    ),
    Mutation(
        "ST2",
        "port order at a shared face ignores the shared stretch rule",
        GATES,
        "if (inner_.slot > outer_.slot) != order_.inner_is_right:",
        "if False:",
    ),
    Mutation(
        "ST3",
        "a shared stretch keeps the channels where the routes only touch",
        STRUCTURE_STRETCHES,
        "while length > 0 and overlap(length - 1) <= 0:",
        "while False:",
    ),
    Mutation(
        "RB1",
        "a foreign line may split a ribbon",
        LANES,
        "        _keep_ribbons(half_segments_, before_, free_, forced_pairs)\n",
        "",
    ),
    Mutation(
        "GR1",
        "a vertical size is off the lane grid",
        GEOMETRY,
        "        return self.node_height_pitches * self.lane_pitch\n",
        "        return self.node_height_pitches * self.lane_pitch - 4\n",
    ),
    Mutation(
        "GR2",
        "vertical channel without the lane clearance",
        GEOMETRY,
        "    return horizontal_channel_size(lane_count, config)\n",
        "    return max(config.min_channel_size, (lane_count + 1) * config.lane_pitch)\n",
    ),
    Mutation(
        "XC1",
        "the lane height of a child container ignores its header",
        STRUCTURE_GEOMETRY,
        "        child_top = self.config.container_header_height\n",
        "        child_top = 0.0\n",
    ),
    Mutation(
        "XC2",
        "a through pass loses the space under a container column",
        STRUCTURE_ROUTING,
        "        candidates: List[StructureChannelId] = [\n"
        "            StructureChannelId(ChannelKind.BOTTOM_CORRIDOR, container_id)\n"
        "        ]",
        "        candidates: List[StructureChannelId] = (\n"
        "            [StructureChannelId(ChannelKind.BOTTOM_CORRIDOR, container_id)]\n"
        "            if not column.is_composite\n"
        "            else []\n"
        "        )",
    ),
    Mutation(
        "XC3",
        "a segment under the columns continues straight without a lane",
        STRUCTURE_ROUTING,
        "        if channel.kind is ChannelKind.BOTTOM_CORRIDOR:\n"
        "            # A segment under the columns",
        "        if False:\n            # A segment under the columns",
    ),
    Mutation(
        "XC4",
        "a parent line does not enter the outer vertical channel of a child",
        STRUCTURE_ROUTING,
        "                result.setdefault(child_vertical_, []).append(corridor_)\n"
        "                result.setdefault(corridor_, []).append(child_vertical_)\n",
        "",
    ),
    Mutation(
        "XC7",
        "a side entry ignores the top corridor of the section",
        STRUCTURE_GEOMETRY,
        "        return self.config.container_header_height + self._channel_size(",
        "        return -math.inf + 0 * self._channel_size(",
    ),
    Mutation(
        "XC8",
        "paths of equal cost do not prefer the common container",
        STRUCTURE_ROUTING,
        "                        if channel_.container_id != common_id\n",
        "                        if False\n",
    ),
    Mutation(
        "XC5",
        "the columns under a segment include the child it enters",
        STRUCTURE_ROUTING,
        "        frame = self.estimate.node_rects[child_id]\n"
        "        return frame.x if vertical.index == 0 else frame.x + frame.width\n",
        "        return x\n",
    ),
    Mutation(
        "SR3",
        "far end of a horizontal segment seen from the wrong side",
        STRUCTURE_ROUTING,
        "other = position + 1 if seen_from == position - 1 else position - 1",
        "other = position - 1 if seen_from == position - 1 else position + 1",
    ),
    Mutation(
        "Z11",
        "debug layer without the pass ports",
        SERIALIZER,
        "                pass_ports=_structure_pass_ports(edge_paths, geometry),\n",
        "",
    ),
    Mutation(
        "CL1",
        "column lane count rule ignores the lane reuse between the sides",
        STRUCTURE_ROUTING,
        "max(left_, right_) + across_",
        "left_ + right_ + across_",
    ),
    Mutation(
        "TP3",
        "through pass into a column channel at another height",
        STRUCTURE_ROUTING,
        "or _center_y(self.channel_rects[candidate_]) == y",
        "or True",
    ),
    Mutation(
        "TP4",
        "through pass under a column that is too low",
        STRUCTURE_GEOMETRY,
        "for height_ in through_heights if height_ >= lowest",
        "for height_ in through_heights",
    ),
    Mutation(
        "NE1",
        "right-hand traffic does not yield to a nested segment",
        LANES,
        "                moved.add(inner_.key)\n",
        "                pass\n",
    ),
    Mutation(
        "Z10",
        "container drawn as a simple node",
        SERIALIZER,
        "        if header_rect_ is None:",
        "        if True:",
    ),
    Mutation(
        "Z1",
        "type without a style does not fall back to default",
        SERIALIZER,
        "type_id_, relation_types[DEFAULT_RELATION_TYPE]",
        "type_id_, relation_types[DANGER_RELATION_TYPE]",
    ),
    Mutation(
        "Z2",
        "warning wins over danger",
        SERIALIZER,
        "    if edge.cycle_id is not None:\n"
        "        return DANGER_RELATION_TYPE\n"
        "    if edge.edge_id in structure.skip_edge_ids:\n"
        "        return WARNING_RELATION_TYPE",
        "    if edge.edge_id in structure.skip_edge_ids:\n"
        "        return WARNING_RELATION_TYPE\n"
        "    if edge.cycle_id is not None:\n"
        "        return DANGER_RELATION_TYPE",
    ),
    Mutation(
        "Z3",
        "relation across levels keeps its input type",
        SERIALIZER,
        "    if edge.edge_id in structure.skip_edge_ids:\n"
        "        return WARNING_RELATION_TYPE",
        "",
    ),
    Mutation(
        "Z4",
        "cycle gets a warning sign",
        SERIALIZER,
        "        if diagnostic_.kind is DiagnosticKind.CYCLE:\n"
        "            continue",
        "",
    ),
    Mutation(
        "Z5",
        "debug attributes written without the debug mode",
        SERIALIZER,
        "_levels_debug_attributes(routing) if debug else {},",
        "_levels_debug_attributes(routing),",
    ),
    Mutation(
        "Z6",
        "type style rule not scoped by the SVG ID",
        SERIALIZER,
        'f"#{svg_id} .{CSS_PREFIX}-edge--type-{index_} "',
        'f".{CSS_PREFIX}-edge--type-{index_} "',
    ),
    Mutation(
        "Z7",
        "coordinates keep trailing zeros",
        SERIALIZER,
        'text = f"{round(value, 2):.2f}".rstrip("0").rstrip(".")',
        'text = f"{round(value, 2):.2f}"',
    ),
    Mutation(
        "Z9",
        "serializer ignores the configuration of the geometry",
        SERIALIZER,
        'markerWidth="{_number(config.arrow_length)}"',
        'markerWidth="{_number(6)}"',
    ),
    Mutation(
        "Z8",
        "node link attribute missing",
        SERIALIZER,
        "        if node_.link is not None:\n            attributes_.append(",
        "        if False:\n            attributes_.append(",
    ),
)


def main() -> None:
    selected_identifiers = set(sys.argv[1:])
    mutations = [
        mutation_
        for mutation_ in MUTATIONS
        if len(selected_identifiers) == 0
        or mutation_.identifier in selected_identifiers
    ]

    has_problems = False
    failed_tests_by_mutation: Dict[str, List[str]] = {}
    for mutation_ in mutations:
        failed_tests_ = _run_mutation(mutation_)
        if failed_tests_ is None:
            print(  # noqa: T201
                f"{mutation_.identifier}: code not found: "
                f"{mutation_.description}"
            )
            has_problems = True
            continue
        failed_tests_by_mutation[mutation_.identifier] = failed_tests_
        print(  # noqa: T201
            f"{mutation_.identifier} ({mutation_.description}): "
            f"{len(failed_tests_)} failing tests"
        )
        for test_name_ in failed_tests_:
            print(f"    {test_name_}")  # noqa: T201

    uncaught = [
        identifier_
        for identifier_, failed_tests_ in failed_tests_by_mutation.items()
        if len(failed_tests_) == 0
    ]
    if len(uncaught) > 0:
        print(f"Mutations that fail no test: {uncaught}")  # noqa: T201
        has_problems = True

    if len(selected_identifiers) == 0:
        caught_tests: Set[str] = {
            test_name_
            for failed_tests_ in failed_tests_by_mutation.values()
            for test_name_ in failed_tests_
        }
        unverified = sorted(set(_all_test_names()) - caught_tests)
        if len(unverified) > 0:
            print(f"Tests that no mutation fails: {unverified}")  # noqa: T201
            has_problems = True

    sys.exit(1 if has_problems else 0)


def _run_mutation(mutation: Mutation) -> Optional[List[str]]:
    """
    Apply a mutation, run the tests, and restore the file.

    Return the names of the failing tests, or None if the mutation does not
    find its code.
    """

    with open(mutation.path, encoding="utf-8") as source_file:
        source = source_file.read()
    if source.count(mutation.original) != 1:
        return None

    backup_path = mutation.path + ".mutation_backup"
    # The backup keeps the modification time (shutil.copy2), so the restored
    # file matches its original bytecode cache.
    shutil.copy2(mutation.path, backup_path)
    try:
        with open(mutation.path, "w", encoding="utf-8") as source_file:
            source_file.write(
                source.replace(mutation.original, mutation.replacement)
                + mutation.appendix
            )
        return _run_tests()
    finally:
        shutil.move(backup_path, mutation.path)


def _run_tests() -> List[str]:
    """
    Run the unit tests of the generator and return the failing test names.

    The tests run without writing bytecode. Python validates a bytecode cache
    by the modification time in whole seconds and by the size of the source.
    A mutation of the same size, written and restored within one second,
    would otherwise stay active in the cache.
    """

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "no:seleniumbase",
            "-q",
            "-rf",
            TESTS_PATH,
        ],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    failed_tests = {
        re.sub(r"\[.*", "", line_.split("::")[-1].split(" ")[0])
        for line_ in result.stdout.splitlines()
        if line_.startswith("FAILED")
    }
    return sorted(failed_tests)


def _all_test_names() -> List[str]:
    test_names: List[str] = []
    tests_directory = os.path.join(TESTS_PATH, "svg_graph")
    for file_name_ in sorted(os.listdir(tests_directory)):
        if not file_name_.startswith("test_") or not file_name_.endswith(".py"):
            continue
        with open(
            os.path.join(tests_directory, file_name_), encoding="utf-8"
        ) as test_file_:
            test_names.extend(
                re.findall(r"^def (test_\w+)", test_file_.read(), re.MULTILINE)
            )
    return test_names


if __name__ == "__main__":
    main()
