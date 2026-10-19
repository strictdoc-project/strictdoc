from markupsafe import Markup, escape


class TextToHtmlWriter:
    @staticmethod
    def write(text_fragment: str) -> Markup:
        return escape(text_fragment).replace("\n", Markup("<br/>\n"))

    @staticmethod
    def write_anchor_link(title: str, href: str, with_icon: bool = True) -> str:
        icon = "🔗&nbsp;" if with_icon else ""
        return f'<a href="{href}">{icon}{title}</a>'
