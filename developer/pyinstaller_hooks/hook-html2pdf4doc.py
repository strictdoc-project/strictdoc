# https://stackoverflow.com/a/64473931/598057
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# The following ensures that the HTML2PDF4Doc.js file is present in the
# PyInstaller bundle of StrictDoc.
datas = collect_data_files("html2pdf4doc")

# Selenium's webdriver modules are imported lazily via selenium.webdriver's
# __getattr__, so PyInstaller does not always detect them automatically.
hiddenimports = collect_submodules("selenium.webdriver")
