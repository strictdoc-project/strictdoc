from markupsafe import Markup


class HTMLFragmentWriter:
    @staticmethod
    def write(text_fragment: str) -> Markup:
        return Markup(text_fragment)

    @staticmethod
    def write_anchor_link(title: str, href: str, with_icon: bool = True) -> str:
        icon = "🔗&nbsp;" if with_icon else ""
        return f'<a href="{href}">{icon}{title}</a>'
