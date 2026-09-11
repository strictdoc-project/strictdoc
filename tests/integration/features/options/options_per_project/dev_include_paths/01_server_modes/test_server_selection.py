import os
import sys

from strictdoc import environment
from strictdoc.commands.server_config import ServerCommandConfig
from strictdoc.core.file_system.document_finder import DocumentFinder
from strictdoc.core.project_config import ProjectConfigLoader
from strictdoc.helpers.parallelizer import Parallelizer


def load_server_documents(project_root: str, development: bool):
    environment.is_development_mode = development
    server_config = ServerCommandConfig(
        debug=True,
        development=development,
        command="server",
        input_path=project_root,
        output_path=os.path.join(project_root, "output"),
        config=None,
        reload=False,
        host=None,
        port=None,
        watch=True,
    )
    project_config = ProjectConfigLoader.load_using_server_config(server_config)
    parallelizer = Parallelizer.create(False)
    try:
        document_tree, asset_manager = DocumentFinder.find_sdoc_content(
            project_config, parallelizer
        )
    finally:
        parallelizer.shutdown()

    document_titles = [
        document.title for document in document_tree.document_list
    ]
    asset_paths = [
        asset_dir.relative_path.relative_path_posix
        for asset_dir in asset_manager.iterate()
    ]
    return document_titles, asset_paths


project_root_ = os.path.abspath(sys.argv[1])

user_titles_, user_assets_ = load_server_documents(project_root_, False)
assert user_titles_ == ["Visible document"]
assert user_assets_ == []

dev_titles_, dev_assets_ = load_server_documents(project_root_, True)
assert sorted(dev_titles_) == ["Development document", "Visible document"]
assert len(dev_assets_) == 1
assert dev_assets_[0].endswith("developer/test_documents/_assets")

environment.is_development_mode = False
