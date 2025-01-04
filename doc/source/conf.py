# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
from pathlib import Path

#sys.path.insert(0, str(Path('..', 'src').resolve()))
sys.path.insert(0, os.path.abspath('../../src'))

#graphviz_dot  = 'C:\Program Files\Graphviz\dot.exe'
project = 'FocusMe'
copyright = '2024, Marcus Boumans'
author = 'Marcus Boumans'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.graphviz',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.plantuml',
    'sphinx.ext.napoleon',
    "sphinx_needs",
]



on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    plantuml = 'java -Djava.awt.headless=true -jar /usr/share/plantuml/plantuml.jar'
else:
    plantuml = 'java -jar %s' % os.path.join(os.path.dirname(__file__), "utils", "plantuml.jar")

    plantuml_output_format = 'png'

# HTML-Theme
html_theme = 'alabaster'

# Optionen für autodoc
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'private-members': True,
    'show-inheritance': True,
}
autodoc_member_order = 'bysource'



needs_diagram_template = 'modern'  # Stil für Diagramme
needs_types = [
    {"directive": "req", "title": "Requirement", "prefix": "R_", "color": "#BFD8D2"},
    {"directive": "spec", "title": "Specification", "prefix": "S_", "color": "#D3F4A9"},
    {"directive": "test", "title": "Test Case", "prefix": "T_", "color": "#F9EB4C"},
    {"directive": "needs", "title": "Need", "prefix": "N_", "color": "#F7EB4C"},
]


templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
