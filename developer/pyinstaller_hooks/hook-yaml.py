from PyInstaller.utils.hooks import copy_metadata

# https://stackoverflow.com/a/64473931/598057
# https://github.com/pyinstaller/pyinstaller/issues/8003#issuecomment-1760270530
datas = copy_metadata("PyYAML")
