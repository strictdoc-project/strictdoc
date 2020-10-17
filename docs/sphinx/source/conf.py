# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'StrictDoc'
copyright = '2020, Stanislav Pankevich'
author = 'Stanislav Pankevich'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

master_doc = 'index'

# -- Options for PDF/TEX output
latex_engine = 'xelatex'

latex_logo = '_static/logo.jpg'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'StrictDoc.tex', 'StrictDoc',
     None, 'book')
]

# - \usepackage[utf8x]{inputenc} enables UTF-8 support.
# - 'extraclassoptions': 'openany,oneside' removes second blank page.
latex_elements = {
    'extraclassoptions': 'openany,oneside',
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',
    # 'pointsize': '14pt' # does not have any effect

    'releasename': "",

    'sphinxsetup': \
        'hmargin={0.7in,0.7in}, vmargin={1in,1in}, \
        verbatimwithframe=true, \
        TitleColor={rgb}{0,0,0}, \
        InnerLinkColor={rgb}{0.1,0.1,0.1}, \
        OuterLinkColor={rgb}{1,0,0}',

    # Roboto is also a good choice.
    # sudo apt install fonts-roboto
    'fontpkg': r'''
        \setmainfont{DejaVu Sans}
        \setsansfont{DejaVu Sans}
        \setmonofont{DejaVu Sans Mono}
    ''',

    # Disable default Sphinx styles for the TOC.
    'tableofcontents': ' ',

    'preamble': r'''
        \usepackage{datetime}
        \usepackage{hyperref}
        \usepackage{fancyhdr}
        \usepackage{makecell}

        \setcounter{secnumdepth}{10}
        \setcounter{tocdepth}{10}
        
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

        % "Since the first page of a chapter uses (by design) the plain style, you need to redefine this style:"
        % https://tex.stackexchange.com/a/157006/61966
        \fancypagestyle{plain}{
            \fancyhf{}
            \fancyhead[R]{
                \textnormal{\nouppercase{StrictDoc}}
                \textcolor{red}{\textbf{Draft}}
                % trim: left top
                % \vspace*{0.4cm}{\includegraphics[trim=-1cm 1.15cm 0 -0cm, scale=.35]{PTS_bow.png}}
            }
            \fancyfoot[R]{
                \thepage
            }
            \renewcommand{\headrulewidth}{0.0pt}
            \renewcommand{\footrulewidth}{1.0pt}
        }

        \fancypagestyle{normal}{
            \fancyhf{}
            \fancyhead[R]{
                \textnormal{\nouppercase{StrictDoc}} 
                \textcolor{red}{\textbf{Draft}}
                % \vspace*{0.4cm}{\includegraphics[trim=-1cm 1.15cm 0cm 0cm, scale=.35]{PTS_bow.png}}
            }
            \fancyfoot[R]{
                \thepage
            }
            \renewcommand{\headrulewidth}{1.0pt}
            \renewcommand{\footrulewidth}{1.0pt}
        }

        \newcommand{\tablecell}[1] {{{#1}}}
    ''',

    'maketitle': r'''
        \pagenumbering{Roman} %%% to avoid page 1 conflict with actual page 1

        \begin{titlepage}   
            \vspace*{50mm} %%% * is used to give space from top

            \begin{flushright}

                \Huge{\textbf{StrictDoc}}
                
                \Large{\textbf{Technical documentation control software}}
            \end{flushright}

            \vspace{30mm}

            \begin{flushright}
                \bgroup
                    \def\arraystretch{1.5}%  1 is the default, change whatever you need
                    \begin{tabular}{|l|l|}
                    \hline
                    \textbf{{Project goal:}} & 
                    \makecell[l]{ 
                            Requirements management, Documentation Control
                    } 
                    \\ \hline
                    \textbf{{Supported Documents:}} & \tablecell {Requirements document, Specification, Technical Manual} \\ \hline
                    \textbf{{Export formats:}} & \tablecell {RST/Sphinx, HTML, PDF} \\ \hline
                    \textbf{{License model:}} & \tablecell {Open source software, Apache 2 license} \\ \hline
                    \textbf{{Project page:}} & \tablecell {https://github.com/stanislaw/strictdoc} \\ \hline
                    \textbf{{Release date:}} & \tablecell {\MonthYearFormat\today} \\ \hline
                    \textbf{{Version:}} & \tablecell {0.0.1} \\ \hline
                    \end{tabular}
                \egroup
            \end{flushright}

            %% \vfill adds at the bottom
            \vfill 

            \begin{center}
                \Large{© 2020 StrictDoc Project}
            \end{center}

        \end{titlepage}

        \clearpage
        
        \pagenumbering{roman}
        \tableofcontents
        %% \listoffigures
        %% \listoftables
        \clearpage
        \pagenumbering{arabic}
        '''
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']