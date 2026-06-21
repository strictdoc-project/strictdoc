from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title='Test project with a host "localhost" and a port 51000',
        server_host="localhost",
        server_port=51000,
    )
    return config
