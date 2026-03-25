import re


def expand_assets_macro(text: str, assets_path: str) -> str:
    """
    Expands the @assets/ macro to the _assets folder in the project root.
    Ignores instances inside backticks or escaped with a backslash.
    """
    if "@assets/" not in text:
        return text

    # Smart replacement ignoring backticks and backslashes
    text = re.sub(r"(?<![`\\])@assets/", assets_path, text)

    # Clean up explicit escapes
    text = text.replace("\\@assets/", "@assets/")

    return text
