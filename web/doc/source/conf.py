#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# -- Path setup --------------------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('../../..'))


# -- Project information -----------------------------------------------------

project = u'ICNML'
copyright = u'2021, Marco De Donno; Christophe Champod; Heidi Eldridge'
author = u'Marco De Donno; Christophe Champod; Heidi Eldridge'

version = u''
release = u''

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']

source_suffix = '.rst'

master_doc = 'index'

language = None

exclude_patterns = []

pygments_style = None

# -- Options for HTML output -------------------------------------------------

html_theme = 'classic'
html_static_path = ['_static']

# -- Options for HTMLHelp output ---------------------------------------------

htmlhelp_basename = 'ICNMLdoc'

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    'papersize': 'a4paper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, 'ICNML.tex', u'ICNML Documentation', u'Marco De Donno; Christophe Champod; Heidi Eldridge', 'manual'),
]


# -- Options for manual page output ------------------------------------------

man_pages = [
    (master_doc, 'icnml', u'ICNML Documentation', [author], 1)
]

