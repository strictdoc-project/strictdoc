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
    'pointsize': '10pt',

    'releasename': "RELLLL",

    # Additional stuff for the LaTeX preamble.
    #
    'preamble': r'''
        \setcounter{secnumdepth}{10}
        \setcounter{tocdepth}{10}
        
        \usepackage{datetime}
        \newdateformat{MonthYearFormat}{%
            \monthname[\THEMONTH], \THEYEAR}

        \pagecolor [RGB]{255, 255, 255}

        \newcommand{\tablecell}[1] {\Large{\texttt{#1}}}
    ''',

    'maketitle': r'''
        \pagenumbering{Roman} %%% to avoid page 1 conflict with actual page 1

        \begin{titlepage}   
            %% \centering
            \begin{flushright}

                \vspace*{40mm} %%% * is used to give space from top

                \Huge{\textbf{StrictDoc}}
                
                \Large{\textbf{Release: 0.0.1 (\MonthYearFormat\today)}}

                \vspace{10mm}

                \begin{tabular}{|l|l|}
                \hline
                \tablecell {Requirements and Specifications} & \tablecell {Documentation Control} \\ \hline
                \tablecell {Traceability and Coverage} & \tablecell {Open source software} \\ \hline
                \end{tabular}

                %% \begin{figure}[!h]
                %%     \centering
                %%     \includegraphics[scale=0.5]{logo.jpg}
                %% \end{figure}
            \end{flushright}

            %% \vfill adds at the bottom
            \vfill 

            \centering

            \Large \textbf{© 2020 \href{https://github.com/stanislaw/strictdoc}{StrictDoc Project}}

        \end{titlepage}

        \clearpage
        
        \pagenumbering{roman}
        \tableofcontents
        %% \listoffigures
        %% \listoftables
        \clearpage
        \pagenumbering{arabic}
        ''',
    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
    'sphinxsetup': \
        'hmargin={0.7in,0.7in}, vmargin={1in,1in}, \
        verbatimwithframe=true, \
        TitleColor={rgb}{0,0,0}, \
        HeaderFamily=\\sffamily\\mdseries, \
        InnerLinkColor={rgb}{0,0,1}, \
        OuterLinkColor={rgb}{0,0,1}',

    'tableofcontents': ' ',
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