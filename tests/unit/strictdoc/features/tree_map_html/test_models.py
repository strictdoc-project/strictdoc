import json

from strictdoc.features.tree_map_html.models import (
    TreeMap,
    TreeMapData,
    TreeMapNode,
)


def test_tree_map_data_serializes_nested_nodes_to_json() -> None:
    requirement_node = TreeMapNode(
        label="Requirement one: ä",
        weight=1,
        color="#aaffaa",
        children=(),
    )
    root_node = TreeMapNode(
        label="Project",
        weight=1,
        color=None,
        children=(requirement_node,),
    )
    tree_map_data = TreeMapData(
        tree_maps=(
            TreeMap(
                title="Document tree map",
                root=root_node,
            ),
        )
    )

    serialized_data = json.loads(tree_map_data.to_json())

    assert serialized_data == {
        "tree_maps": [
            {
                "title": "Document tree map",
                "root": {
                    "label": "Project",
                    "weight": 1,
                    "color": None,
                    "children": [
                        {
                            "label": "Requirement one: ä",
                            "weight": 1,
                            "color": "#aaffaa",
                            "children": [],
                        }
                    ],
                },
            }
        ]
    }
