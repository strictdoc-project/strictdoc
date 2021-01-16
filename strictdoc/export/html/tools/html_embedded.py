import os

import bs4
from bs4 import BeautifulSoup
from datauri import DataURI


class EmbeddableTag:
    CSS = "css"
    JS = "js"
    IMAGE_PNG = "image_png"
    IMAGE_SVG = "image_svg"

    MAP = {
        CSS: {"attr": "href", "type": "text/css"},
        JS: {"attr": "src", "type": "text/javascript"},
        IMAGE_PNG: {"attr": "src", "type": "image/png"},
        IMAGE_SVG: {"attr": "data", "type": "image/svg+xml"},
    }

    def __init__(self, asset_type, path):
        assert asset_type
        assert path
        self.asset_type = asset_type
        self.path = path

    @staticmethod
    def recognize_from_soup_tag(tag: bs4.element.Tag):
        if tag.name == "link":
            if "rel" in tag.attrs:
                rel_value = tag.attrs["rel"][0]
                if rel_value == "stylesheet":
                    return EmbeddableTag(EmbeddableTag.CSS, tag.attrs["href"])
        elif tag.name == "script":
            if "type" in tag.attrs:
                type_value = tag.attrs["type"]
                if type_value == "text/javascript":
                    return EmbeddableTag(EmbeddableTag.JS, tag.attrs["src"])
        elif tag.name == "img":
            if "src" in tag.attrs:
                rel_value: str = tag.attrs["src"]
                if rel_value.lower().endswith(".png"):
                    return EmbeddableTag(
                        EmbeddableTag.IMAGE_PNG, tag.attrs["src"]
                    )
        elif tag.name == "object":
            if "type" in tag.attrs:
                type_value = tag.attrs["type"]
                if type_value == "image/svg+xml":
                    return EmbeddableTag(
                        EmbeddableTag.IMAGE_SVG, tag.attrs["data"]
                    )
        return None

    def get_path(self):
        return self.path

    def get_attr(self):
        return EmbeddableTag.MAP[self.asset_type]["attr"]

    def get_type(self):
        return EmbeddableTag.MAP[self.asset_type]["type"]


class HTMLEmbedder:
    @staticmethod
    def embed_assets(html_string, path):
        soup = BeautifulSoup(html_string, "html5lib")

        tag: bs4.element.Tag
        for tag in soup.findAll(recursive=True):
            embeddable_tag = EmbeddableTag.recognize_from_soup_tag(tag)
            if not embeddable_tag:
                continue
            output_dir = os.path.dirname(path)
            asset_path = os.path.join(output_dir, embeddable_tag.get_path())
            tag.attrs[
                embeddable_tag.get_attr()
            ] = HTMLEmbedder._read_file_as_base64(asset_path)

        output = str(soup)
        return output

    @staticmethod
    def _read_file_as_base64(asset_path):
        # DataURI.from_file seems to work well without knowing content type.
        # There is also a lower-level DataURI.make file.
        base64 = DataURI.from_file(asset_path)
        return base64
