import distutils.log
import distutils.dir_util
import os


def sync_dir(src_dir, dst_dir):
    assert os.path.isabs(src_dir), f"Expected {src_dir} to be an absolute path"
    assert os.path.isdir(src_dir), f"Expected {src_dir} to be a directory"
    distutils.log.set_verbosity(distutils.log.DEBUG)
    distutils.dir_util.copy_tree(
        src_dir,
        dst_dir,
        update=1,
        verbose=1,
    )
