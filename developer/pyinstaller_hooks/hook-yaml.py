from PyInstaller.utils.hooks import collect_all

# https://stackoverflow.com/a/64473931/598057
datas, binaries, hiddenimports = collect_all("PyYAML")
