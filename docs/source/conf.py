import os
import sys
import time
from unittest.mock import MagicMock

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MECHA03 ROMI'
copyright = '2025, Col Cook, Nathan Neugeboren'
author = 'Col Cook, Nathan Neugeboren'
release = '0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    "sphinxcontrib.video",
]

if 'sphinx' in sys.modules:
    time.ticks_us = MagicMock(return_value=12345678)
    time.ticks_ms = MagicMock(return_value=12345678)
    time.ticks_diff = MagicMock(return_value=12345678)
    time.ticks_add = MagicMock(return_value=12345678)

autodoc_mock_imports = ['pyb','time','micropython']
autoclass_content = 'both'

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

sys.path.insert(0, os.path.abspath('../../Drivers'))