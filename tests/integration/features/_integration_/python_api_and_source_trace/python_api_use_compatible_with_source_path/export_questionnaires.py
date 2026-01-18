import argparse
import os

from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export questionnaires from SDoc documents."
    )

    parser.add_argument(
        "input_path",
        type=str,
        help="Path to the input path."
    )

    # Optional argument
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Optional directory to save output."
    )

    args = parser.parse_args()

    input_path = args.input_path
    output_dir = args.output_dir

    project_config: ProjectConfig = ProjectConfigLoader.load(
        input_path=input_path, output_dir=output_dir
    )
    # Verify that the source root path is resolved from the original form "src"
    # to an absolute path. This confirms that the project config is correctly
    # validated and finalized.
    assert os.path.isabs(project_config.source_root_path), project_config.source_root_path
