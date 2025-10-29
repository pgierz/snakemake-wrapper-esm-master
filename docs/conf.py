# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from unittest.mock import MagicMock

# Add parent directory to path so we can import the wrapper modules
sys.path.insert(0, os.path.abspath('..'))

# Mock the snakemake object that is injected at runtime
# This allows wrapper.py files to be imported without errors
class MockSnakemake:
    """Mock snakemake object for documentation building."""

    class _MockDict(dict):
        """Mock dict that returns empty string for any missing key."""
        def __getitem__(self, key):
            return self.get(key, "")

    params = _MockDict()
    input = []
    output = []
    log = []
    resources = {}
    wildcards = {}
    threads = 1

    @staticmethod
    def log_fmt_shell(stdout=True, stderr=True):
        return ""

# Inject mock snakemake object into builtins so wrapper.py can import
import builtins
builtins.snakemake = MockSnakemake()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Snakemake ESM-Tools Wrappers'
copyright = '2025, Paul Gierz'
author = 'Paul Gierz'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'myst_nb',  # Replaces myst_parser and adds eval-rst support
    'sphinx_copybutton',
    'sphinx_design',  # For grid directive
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_title = 'Snakemake ESM-Tools Wrappers'

html_theme_options = {
    'repository_url': 'https://github.com/pgierz/snakemake-wrapper-esm-master',
    'use_repository_button': True,
    'use_issues_button': True,
    'use_edit_page_button': True,
    'path_to_docs': 'docs',
}

# -- Extension configuration -------------------------------------------------

# Napoleon settings for Google/NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'snakemake': ('https://snakemake.readthedocs.io/en/stable', None),
}

# MyST parser settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Enable eval-rst directive for autodoc in MyST
myst_dmath_double_inline = True
