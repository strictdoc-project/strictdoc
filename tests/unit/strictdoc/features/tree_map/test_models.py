import json

from strictdoc.features.tree_map.models import (
    TreeMap,
    TreeMapData,
    TreeMapLegendItem,
    TreeMapNode,
)


def test_tree_map_data_serializes_nested_nodes_to_json() -> None:
    requirement_node = TreeMapNode(
        identifier="MID-1",
        label="Requirement one: ä",
        count=42,
        weight=1,
        color="#aaffaa",
        children=(),
        title="Requirement one",
        mid="MID-1",
        uid="REQ-1",
        document_url="input.html#REQ-1",
        preview_url="/actions/show_full_node?reference_mid=MID-1",
    )
    root_node = TreeMapNode(
        identifier="project",
        label="Project",
        count=None,
        weight=1,
        color=None,
        children=(requirement_node,),
    )
    tree_map_data = TreeMapData(
        tree_maps=(
            TreeMap(
                identifier="document-tree",
                title="Document tree map",
                description="Map description.",
                legend=(TreeMapLegendItem(color="#aaffaa", text="Covered"),),
                root=root_node,
            ),
        )
    )

    serialized_data = json.loads(tree_map_data.to_json())

    assert serialized_data == {
        "tree_maps": [
            {
                "identifier": "document-tree",
                "title": "Document tree map",
                "description": "Map description.",
                "legend": [{"color": "#aaffaa", "text": "Covered"}],
                "root": {
                    "identifier": "project",
                    "label": "Project",
                    "count": None,
                    "weight": 1,
                    "color": None,
                    "title": None,
                    "mid": None,
                    "uid": None,
                    "document_url": None,
                    "preview_url": None,
                    "children": [
                        {
                            "identifier": "MID-1",
                            "label": "Requirement one: ä",
                            "count": 42,
                            "weight": 1,
                            "color": "#aaffaa",
                            "title": "Requirement one",
                            "mid": "MID-1",
                            "uid": "REQ-1",
                            "document_url": "input.html#REQ-1",
                            "preview_url": (
                                "/actions/show_full_node?reference_mid=MID-1"
                            ),
                            "children": [],
                        }
                    ],
                },
            }
        ]
    }
