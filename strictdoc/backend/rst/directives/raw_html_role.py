from typing import Any, Dict, List, Optional, Tuple

from docutils import nodes
from docutils.parsers.rst.states import Inliner


def raw_html_role(
    _name: str,
    _rawtext: str,
    text: str,
    _lineno: int,
    _inliner: Inliner,
    _options: Optional[Dict[str, Any]] = None,
    _content: Optional[List[str]] = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    html = nodes.raw(text, text, format="html")
    return [html], []
