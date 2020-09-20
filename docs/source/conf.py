# -*- coding: utf-8 -*-

import sys

import mock
import sphinx_rtd_theme
from sphinx.ext import autodoc

PACKAGE_NAME = "PixelPi Library"
PACKAGE_HANDLE = "PixelPi"
PACKAGE_MODULE = "Strip"
PACKAGE_COPYRIGHT = "2020, Hut 8 Designs"
PACKAGE_AUTHOR = "Geeky Tim"

# Prompte /usr/local/lib to the front of sys.path
# sys.path.insert(0,site.getsitepackages()[0])

sys.modules['RPi'] = mock.Mock()
sys.modules['RPi.GPIO'] = mock.Mock()
sys.modules['rpi_ws281x'] = mock.Mock()
sys.modules['gpiozero'] = mock.Mock()
sys.modules['PIL'] = mock.Mock()
sys.modules['atexit'] = mock.Mock()

sys.path.insert(0, '../../library')
from pixelpi import Strip


class OutlineMethodDocumenter(autodoc.MethodDocumenter):
    objtype = 'method'

    def add_content(self, more_content, no_docstring=False):
        return


class OutlineFunctionDocumenter(autodoc.FunctionDocumenter):
    objtype = 'function'

    def add_content(self, more_content, no_docstring=False):
        return


class ModuleOutlineDocumenter(autodoc.ModuleDocumenter):
    objtype = 'moduleoutline'

    def __init__(self, directive, name, indent=u''):
        # Monkey path the Method and Function documenters
        sphinx_app.add_autodocumenter(OutlineMethodDocumenter)
        sphinx_app.add_autodocumenter(OutlineFunctionDocumenter)
        autodoc.ModuleDocumenter.__init__(self, directive, name, indent)

    def __del__(self):
        # Return the Method and Function documenters to normal
        sphinx_app.add_autodocumenter(autodoc.MethodDocumenter)
        sphinx_app.add_autodocumenter(autodoc.FunctionDocumenter)


def setup(app):
    global sphinx_app
    sphinx_app = app
    app.add_autodocumenter(ModuleOutlineDocumenter)

    ModuleOutlineDocumenter.objtype = 'module'


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosectionlabel',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
#
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = PACKAGE_NAME
copyright = PACKAGE_COPYRIGHT
author = PACKAGE_AUTHOR

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'collapse_navigation': False,
    'display_version': True
}

# Add any paths that contain custom themes here, relative to this directory.
html_theme_path = [
    '_themes',
    sphinx_rtd_theme.get_html_theme_path()
]

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#
html_logo = 'images/hut256.png'

# The name of an image file (relative to this directory) to use as a favicon of
# the docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# shift large.
#
html_favicon = 'images/hut256.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If false, no module index is generated.
#
html_domain_indices = True

# If false, no index is generated.
#
html_use_index = True

# If true, the index is split into individual pages for each letter.
#
html_split_index = False

# If true, links to the reST sources are added to the pages.
#
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.green. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr', 'zh'
#
# html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# 'ja' uses this config value.
# 'zh' user can custom change `jieba` dictionary path.
#
# html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#
# html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = PACKAGE_HANDLE + 'doc'

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, PACKAGE_MODULE, PACKAGE_NAME + u' Documentation',
     [author], 1)
]

# If true, show URL addresses after external links.
#
# man_show_urls = False
