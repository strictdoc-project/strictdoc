# https://stackoverflow.com/a/64473931/598057
from PyInstaller.utils.hooks import collect_data_files

# SPDX Tools when writing SPDX to JSON-LD format relies on JSON files stored
# inside the package. The following ensures that these files are present in the
# PyInstaller bundle of StrictDoc.
datas = collect_data_files("spdx_tools")
