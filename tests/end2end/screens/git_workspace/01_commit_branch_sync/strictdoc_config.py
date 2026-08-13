from strictdoc.core.project_config import ProjectConfig


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        # Deliberately outside the repo: an output/ dir nested inside the
        # repo would show up as untracked in "git status" and make
        # is_clean_branch() (and therefore checkout_branch()) think the
        # workspace is dirty.
        dir_for_sdoc_cache="$TMPDIR",
        project_features=["GIT_WORKSPACE_EXPERIMENTAL"],
    )
    return config
