# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import string
import sys

import guzzle_sphinx_theme as guzzle_sphinx_theme

# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.


try:
    strictdoc_root_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    if not os.path.isdir(strictdoc_root_path):
        raise FileNotFoundError
    # Cannot assert this because readthedocs clones strictdoc to folders like:
    # "stable", "latest", etc.
    # assert os.path.basename(strictdoc_root_path) == "strictdoc"
    sys.path.append(strictdoc_root_path)
    import strictdoc
except Exception as exception:
    print(f"Could not resolve a path to strictdoc's root: {exception}")
    sys.exit(1)


# Strings with embedded variables in Python
# https://stackoverflow.com/a/16553401/598057
class RubyTemplate(string.Template):
    delimiter = "#"


STRICTDOC_VERSION = strictdoc.__version__

# -- Project information -----------------------------------------------------

project = "StrictDoc"
copyright = "2022, Stanislav Pankevich"
author = "Stanislav Pankevich"

# The full version, including alpha/beta/rc tags
release = STRICTDOC_VERSION


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["guzzle_sphinx_theme"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

html_extra_path = ["../../strictdoc-html"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

master_doc = "index"

# -- Options for PDF/TEX output
latex_engine = "xelatex"

latex_logo = "_static/logo.jpg"

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [(master_doc, "StrictDoc.tex", "StrictDoc", None, "book")]

# - \usepackage[utf8x]{inputenc} enables UTF-8 support.
# - 'extraclassoptions': 'openany,oneside' removes second blank page.
latex_elements = {
    "extraclassoptions": "openany,oneside",
    # The paper size ('letterpaper' or 'a4paper').
    "papersize": "a4paper",
    # 'pointsize': '14pt' # does not have any effect
    "fncychap": "",  # disable fncychap
    "releasename": "",
    "sphinxsetup": "hmargin={0.7in,0.7in}, vmargin={1in,1in}, \
        verbatimwithframe=true, \
        TitleColor={rgb}{0,0,0}, \
        InnerLinkColor={rgb}{0.1,0.1,0.1}, \
        OuterLinkColor={rgb}{1,0,0}",
    # Roboto is also a good choice.
    # sudo apt install fonts-roboto
    "fontpkg": r"""
        \setmainfont{DejaVu Sans}
        \setsansfont{DejaVu Sans}
        \setmonofont{DejaVu Sans Mono}
    """,
    # Disable default Sphinx styles for the TOC.
    "tableofcontents": " ",
    "preamble": r"""
        \usepackage{datetime}
        \usepackage{hyperref}
        \usepackage{fancyhdr}
        \usepackage{makecell}

        \setcounter{secnumdepth}{10}
        \setcounter{tocdepth}{6}
        
        \newdateformat{MonthYearFormat}{%
            \monthname[\THEMONTH], \THEYEAR}

        \pagecolor [RGB]{255, 255, 255}

        \hypersetup{
            colorlinks=true,
            linkcolor=[RGB]{35, 35, 35}, % color of internal links (change box color with linkbordercolor)
            citecolor=green,        % color of links to bibliography
            filecolor=magenta,      % color of file links
            urlcolor=cyan % This has an effect
        }

        \makeatletter
            % "Since the first page of a chapter uses (by design) the plain style, you need to redefine this style:"
            % https://tex.stackexchange.com/a/157006/61966
            \fancypagestyle{plain}{
                \fancyhf{}
                \fancyhead[R]{
                    \textnormal{\nouppercase{StrictDoc}}
                    % trim: left top
                    % \vspace*{0.4cm}{\includegraphics[trim=-1cm 1.15cm 0 -0cm, scale=.35]{PTS_bow.png}}
                }
                \fancyfoot[R]{
                    \thepage
                }
                \renewcommand{\headrulewidth}{0.0pt}
                \renewcommand{\footrulewidth}{1.0pt}
            }
            \pagestyle{plain}
            \fancypagestyle{normal}{
                \fancyhf{}
                \fancyhead[R]{
                    \textnormal{\nouppercase{StrictDoc}}
                    % \vspace*{0.4cm}{\includegraphics[trim=-1cm 1.15cm 0cm 0cm, scale=.35]{PTS_bow.png}}
                }
                \fancyfoot[R]{
                    \thepage
                }
                \renewcommand{\headrulewidth}{1.0pt}
                \renewcommand{\footrulewidth}{1.0pt}
            }
        \makeatother

        \usepackage{eqparbox}
        \usepackage{titletoc}

        \titlecontents{chapter}
                      [0em]
                      {\vspace{.25\baselineskip}}
                      {\raisebox{0.038cm}{\eqparbox{ch}{\thecontentslabel}\hspace{0.2cm}}}
                      {}
                      {\titlerule*[10pt]{$\cdot$}\contentspage}
        
        \titlecontents{section}
                      [0.5cm]
                      {\vspace{.25\baselineskip}}
                      {\raisebox{0.038cm}{\eqparbox{S}{\thecontentslabel}\hspace{0.2cm}}}
                      {}
                      {\titlerule*[10pt]{$\cdot$}\contentspage}
        
        \titlecontents{subsection}
                      [1cm]
                      {\vspace{.25\baselineskip}}
                      {\raisebox{0.038cm}{\eqparbox{Ss}{\thecontentslabel}\hspace{0.2cm}}}
                      {}
                      {\titlerule*[10pt]{$\cdot$}\contentspage}

        \titlecontents{subsubsection}
                      [1.5cm]
                      {\vspace{.25\baselineskip}}
                      {\raisebox{0.038cm}{\eqparbox{Sss}{\thecontentslabel}\hspace{0.2cm}}}
                      {}
                      {\titlerule*[10pt]{$\cdot$}\contentspage}
        
        \titlecontents{paragraph}
                      [2cm]
                      {\vspace{.25\baselineskip}}
                      {\raisebox{0.038cm}{\eqparbox{par}{\thecontentslabel}\hspace{0.2cm}}}
                      {}
                      {\titlerule*[10pt]{$\cdot$}\contentspage}

        \titlecontents{subparagraph}
                      [2.5cm]
                      {\vspace{.25\baselineskip}}
                      {\raisebox{0.038cm}{\eqparbox{subpar}{\thecontentslabel}\hspace{0.2cm}}}
                      {}
                      {\titlerule*[10pt]{$\cdot$}\contentspage}

        \newcommand{\tablecell}[1] {{{#1}}}
        
        \titleformat{\chapter}[hang] 
            {\normalfont\huge\bfseries}{\thechapter.}{3mm}{} 
        \titlespacing*{\chapter}{0pt}{-24pt}{18pt}

        \makeatletter
            \newcommand\sdocfronttitlefont{\@setfontsize\Huge{36}{36}}
            \newcommand\sdocfrontsubtitlefont{\@setfontsize\Huge{16}{16}}
        \makeatother
    """,
    "maketitle": RubyTemplate(
        r"""
        \pagenumbering{Roman} %%% to avoid page 1 conflict with actual page 1

        \begin{titlepage}   
            \vspace*{50mm} %%% * is used to give space from top

            \begin{center}
                \sdocfronttitlefont{\textbf{StrictDoc}}
                
                \vspace{5mm}

                \sdocfrontsubtitlefont{{Software for writing technical requirements and specifications}}
                % \Large{{management framework}}
            \end{center}

            \vspace{30mm}

            \begin{flushright}
                \bgroup
                    \def\arraystretch{1.9}%  1 is the default, change whatever you need
                    \begin{tabular}{|p{4.85cm}|p{11.7cm}|}
                    \hline
                    \textbf{{Project goals:}} & 
                    \makecell[l]{ 
                            Technical requirements and specifications management, 
                            \\
                            documentation control
                    } 
                    \\ \hline
                    \textbf{{Supported documents:}} & \tablecell {Requirements document/specification, technical manual} \\ \hline
                    \textbf{{Documents storage:}} & \tablecell {Plain text files} \\ \hline
                    \textbf{{Export formats:}} & \tablecell {RST/Sphinx, HTML, PDF, Excel} \\ \hline
                    \textbf{{License model:}} & \tablecell {Open source software, Apache 2 license} \\ \hline
                    \textbf{{Project page:}} & \tablecell {https://github.com/stanislaw/strictdoc} \\ \hline
                    \textbf{{Release date:}} & \tablecell {\MonthYearFormat\today} \\ \hline
                    \textbf{{Version:}} & \tablecell #{STRICTDOC_VERSION} \\ \hline
                    \end{tabular}
                \egroup
            \end{flushright}

            %% \vfill adds at the bottom
            \vfill 

            \begin{center}
                \Large{© 2022 StrictDoc Project}
            \end{center}

        \end{titlepage}

        \clearpage

        \pagenumbering{roman}
        \pagestyle{plain}
        \tableofcontents
        %% \listoffigures
        %% \listoftables
        \clearpage
        \pagestyle{normal}
        \pagenumbering{arabic}
        """
    ).substitute(STRICTDOC_VERSION=STRICTDOC_VERSION),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = "guzzle_sphinx_theme"
html_theme_path = guzzle_sphinx_theme.html_theme_path()

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_css_files = [
    "theme_overrides.css",
]
html_sidebars = {"**": ["globaltoc.html", "searchbox.html"]}
