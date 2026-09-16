from strictdoc.core.project_config import (
    DEPRECATED_FEATURES,
    ProjectConfig,
    ProjectFeature,
)
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.project_configuration.view_object import (
    ProjectConfigurationViewObject,
)
from strictdoc.features.tree_map.feature import TreeMapFeature


def create_view_object(
    project_config: ProjectConfig,
) -> ProjectConfigurationViewObject:
    return ProjectConfigurationViewObject(
        project_config=project_config,
        link_renderer=LinkRenderer(root_path="", static_path="_static"),
    )


def test_01_project_features_display_shows_feature_handles() -> None:
    project_config = ProjectConfig(
        project_features=[
            ProjectFeature.DIFF,
            "REQIF",
            TreeMapFeature(),
        ]
    )

    view_object = create_view_object(project_config)

    assert view_object.project_features_display() == (
        "DIFF, REQIF, TREE_MAP_SCREEN"
    )


def test_02_project_features_display_hides_nestor_and_deprecated() -> None:
    project_config = ProjectConfig(
        project_features=[
            ProjectFeature.NESTOR,
            ProjectFeature.MATHJAX,
            "MERMAID",
            ProjectFeature.SEARCH,
        ]
    )

    view_object = create_view_object(project_config)

    assert view_object.project_features_display() == "SEARCH"


def test_03_project_features_display_all_features() -> None:
    project_config = ProjectConfig(
        project_features=["ALL_FEATURES", ProjectFeature.MATHJAX]
    )

    view_object = create_view_object(project_config)

    displayed_features = view_object.project_features_display()
    assert displayed_features.startswith("<b>ALL_FEATURES:</b><br/> ")
    assert ProjectFeature.SEARCH.value in displayed_features
    assert ProjectFeature.NESTOR.value not in displayed_features
    for feature_ in DEPRECATED_FEATURES:
        assert feature_ not in displayed_features
