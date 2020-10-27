import distutils.log
import distutils.dir_util
import os


def sync_dir(src_dir, dst_dir):
    assert os.path.isdir(src_dir)
    distutils.log.set_verbosity(distutils.log.DEBUG)
    distutils.dir_util.copy_tree(
        src_dir,
        dst_dir,
        update=1,
        verbose=1,
    )
