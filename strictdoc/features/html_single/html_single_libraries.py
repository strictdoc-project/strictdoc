"""
The JavaScript libraries that the single-file HTML export embeds, loads from
a CDN, or replaces with a stub.

The CDN paths and integrity hashes pin the exact versions that StrictDoc
vendors. Mermaid, MathJax and Viz.js are byte-identical to their npm
packages. The vendored plantuml-core.js is a classic-script bundle of the
@plantuml/core package: the CDN loads the package's ES module (plantuml.js)
instead and exposes it as the same global (PlantUMLCore).

When a vendored library is upgraded, update its CDN path and integrity hash
here. A unit test compares the hashes with the vendored files.

@relation(SDOC-SRS-217, scope=file)
"""

import re
from dataclasses import dataclass
from typing import List, Optional, Pattern


@dataclass(frozen=True)
class HTMLSingleScript:
    # The path of the script, relative to StrictDoc's static assets folder.
    static_path: str
    # The path of the script on the CDN, relative to the CDN URL.
    cdn_path: str
    # The Subresource Integrity hash of the CDN file.
    cdn_integrity: str
    # The global variable that receives the exports of an ES module. None for
    # a classic script.
    module_global: Optional[str] = None


@dataclass(frozen=True)
class HTMLSingleLibrary:
    name: str
    # Markup in the exported HTML that the library renders.
    content_marker: Pattern[str]
    scripts: List[HTMLSingleScript]
    # Files and folders, relative to the static assets folder, that the
    # single-file export leaves out when it does not embed the library.
    static_paths: List[str]


HTML_SINGLE_LIBRARIES: List[HTMLSingleLibrary] = [
    HTMLSingleLibrary(
        name="mathjax",
        # The math role and directive render a "math" class. MathJax also
        # renders the TeX delimiters in plain text.
        content_marker=re.compile(
            r'class="(?:[^"]*\s)?math(?:\s[^"]*)?"|\\\(|\\\[|\$\$'
        ),
        scripts=[
            HTMLSingleScript(
                static_path="mathjax/tex-mml-chtml.js",
                cdn_path="mathjax@3.2.0/es5/tex-mml-chtml.js",
                cdn_integrity=(
                    "sha384-"
                    "+BSz3oj3ILMYvOBr16U9i0H4RZRmGyQQ+1q9eqr8T3skmAFrJk8Gmgwg"
                    "qlCZdNSo"
                ),
            ),
        ],
        static_paths=["mathjax/tex-mml-chtml.js", "mathjax/output/"],
    ),
    HTMLSingleLibrary(
        name="mermaid",
        content_marker=re.compile(r'class="(?:[^"]*\s)?mermaid(?:\s[^"]*)?"'),
        scripts=[
            HTMLSingleScript(
                static_path="mermaid/mermaid.min.js",
                cdn_path="mermaid@11.12.2/dist/mermaid.min.js",
                cdn_integrity=(
                    "sha384-"
                    "1ggI9FC3CkghppRD/XCR4aD+jp4DxwXlJIW0wxhyTLNKuiZEW3c4Bwcj"
                    "KXl0iVAJ"
                ),
            ),
        ],
        static_paths=["mermaid/mermaid.min.js"],
    ),
    HTMLSingleLibrary(
        name="plantuml",
        content_marker=re.compile(r'class="(?:[^"]*\s)?plantuml(?:\s[^"]*)?"'),
        scripts=[
            HTMLSingleScript(
                static_path="plantuml/viz-global.js",
                cdn_path="@plantuml/core@1.2026.7/viz-global.js",
                cdn_integrity=(
                    "sha384-"
                    "YulQ1+n4XOro2oW7iXn71KwRuvB3kgfnhF/PoSnkH870b1M89LSBo6SL"
                    "UYzKPSSA"
                ),
            ),
            HTMLSingleScript(
                static_path="plantuml/plantuml-core.js",
                cdn_path="@plantuml/core@1.2026.7/plantuml.js",
                cdn_integrity=(
                    "sha384-"
                    "d8Gw9TAEgs15m95nopH6xLSRhfs5WkvHtoN0Z917nPVk3krOLl/NL7OT"
                    "3swfs51j"
                ),
                module_global="PlantUMLCore",
            ),
        ],
        static_paths=["plantuml/viz-global.js", "plantuml/plantuml-core.js"],
    ),
]
