from tests.end2end.end2end_test_setup import End2EndTestSetup


def write_long_document_with_tall_chunk_above_viewport(
    test_setup: End2EndTestSetup,
) -> None:
    document_parts = [
        "[DOCUMENT]\nTITLE: Chunk Above Viewport Stability Document\n\n"
    ]
    tall_statement = (
        "This node belongs to the tall chunk above the visible target. "
        "It intentionally renders much taller than the lazy placeholder. "
        "The test force-loads this chunk after the target below is visible."
    )
    normal_statement = (
        "This regular node keeps the target area simple and predictable."
    )

    for node_index in range(1, 41):
        uid = f"CAB-{node_index:03d}"
        is_tall_chunk_node = 21 <= node_index <= 30
        statement = (
            "\n\n".join([tall_statement] * 18)
            if is_tall_chunk_node
            else normal_statement
        )
        document_parts.append(
            f"[REQUIREMENT]\n"
            f"UID: {uid}\n"
            f"TITLE: Chunk Above Requirement {node_index}\n"
            f"STATEMENT: >>>\n"
            f"{statement}\n"
            f"<<<\n"
            f"\n"
        )

    test_setup.write_to_sandbox_file(
        "chunk_above.sdoc",
        "".join(document_parts),
    )


def write_long_text_document_with_large_section_subtree(
    test_setup: End2EndTestSetup,
) -> None:
    document_parts = [
        (
            "[DOCUMENT]\n"
            "TITLE: Create Below Large Section Document\n"
            "OPTIONS:\n"
            "  ENABLE_MID: True\n"
            "  NODE_IN_TOC: True\n\n"
            "[GRAMMAR]\n"
            "ELEMENTS:\n"
            "- TAG: SECTION\n"
            "  PROPERTIES:\n"
            "    IS_COMPOSITE: True\n"
            "    PREFIX: None\n"
            "    VIEW_STYLE: Narrative\n"
            "  FIELDS:\n"
            "  - TITLE: MID\n"
            "    TYPE: String\n"
            "    REQUIRED: True\n"
            "  - TITLE: UID\n"
            "    TYPE: String\n"
            "    REQUIRED: False\n"
            "  - TITLE: TITLE\n"
            "    TYPE: String\n"
            "    REQUIRED: True\n"
            "- TAG: TEXT\n"
            "  PROPERTIES:\n"
            "    VIEW_STYLE: Narrative\n"
            "  FIELDS:\n"
            "  - TITLE: MID\n"
            "    TYPE: String\n"
            "    REQUIRED: True\n"
            "  - TITLE: STATEMENT\n"
            "    TYPE: String\n"
            "    REQUIRED: True\n\n"
            "[[SECTION]]\n"
            "MID: 10000000000000000000000000000000\n"
            "UID: CREATE-PARENT\n"
            "TITLE: Section With Large Subtree\n\n"
        )
    ]

    for node_index in range(1, 26):
        document_parts.append(
            f"[TEXT]\n"
            f"MID: {node_index:032x}\n"
            f"STATEMENT: Section child text {node_index}.\n"
            f"\n"
        )

    document_parts.append(
        "[[/SECTION]]\n\n"
        "[[SECTION]]\n"
        "MID: 20000000000000000000000000000000\n"
        "UID: CREATE-NEXT-SECTION\n"
        "TITLE: Next Sibling Section\n\n"
    )

    for node_index in range(1, 16):
        document_parts.append(
            f"[TEXT]\n"
            f"MID: {100 + node_index:032x}\n"
            f"STATEMENT: Following section child text {node_index}.\n"
            f"\n"
        )

    document_parts.append("[[/SECTION]]\n")

    test_setup.write_to_sandbox_file(
        "create_below_large_section.sdoc",
        "".join(document_parts),
    )
