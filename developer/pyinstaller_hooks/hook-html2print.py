# https://stackoverflow.com/a/64473931/598057
from PyInstaller.utils.hooks import collect_data_files

# The following ensures that the HTML2PDF.js file is present in the
# PyInstaller bundle of StrictDoc.
datas = collect_data_files("html2print")
