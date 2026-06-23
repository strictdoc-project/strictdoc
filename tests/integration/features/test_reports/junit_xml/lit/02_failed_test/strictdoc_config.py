from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_features=["REQUIREMENT_TO_SOURCE_TRACEABILITY"],
        test_report_root_dict={
            "reports/tests_integration.lit.junit.xml": "tests/integration",
        },
    )
    return config
