# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os,sys;
sys.path.insert(0, os.path.abspath('../')); 

project = 'AC-DC'
copyright = '2025, Sergio Manthey-Corchado'
author = 'Sergio Manthey-Corchado'
release = 'v1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['myst_parser', 'sphinx.ext.autodoc', 'sphinx.ext.viewcode', 'sphinx.ext.napoleon', 'sphinxemoji.sphinxemoji', 'sphinx_copybutton', 'nbsphinx', "sphinx_plotly_directive",]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = "sphinx_book_theme"
html_title = "AC-DC DOCUMENTATION"
html_theme_options = {
    "home_page_in_toc": True,
    "repository_url": "https://github.com/CIEMAT-Neutrino/AC-DC",
    "repository_branch": "master",
    "path_to_docs": "docs",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
}

myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 2
myst_footnote_transition = True
myst_dmath_double_inline = True
myst_enable_checkboxes = True
