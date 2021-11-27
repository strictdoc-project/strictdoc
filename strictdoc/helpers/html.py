import re

from bs4 import BeautifulSoup


WS_REGEX = re.compile(r"^(\s*)", re.MULTILINE)


# https://stackoverflow.com/a/15513483/598057
def prettify_html_fragment(html_fragment):
    full_soup = BeautifulSoup(html_fragment, features="lxml")

    if full_soup.body:
        soup = full_soup.body.next
    elif full_soup.html:
        soup = full_soup.html.next
    else:
        soup = full_soup
    prettied_html = soup.prettify()
    return WS_REGEX.sub(r"\1" * 2, prettied_html)
