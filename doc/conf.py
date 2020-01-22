import datetime
import os.path

version_file = os.path.join(
    os.path.dirname(__file__),
    '../plyvel/_version.py')
with open(version_file) as fp:
    exec(fp.read(), globals(), locals())

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage']

templates_path = ['_templates']
exclude_patterns = ['_build']
source_suffix = '.rst'

master_doc = 'index'
project = u'Plyvel'
copyright = u'2012‒{}, Wouter Bolsterlee'.format(
    datetime.datetime.now().year)
version = __version__
release = __version__

autodoc_default_options = {"members": True, "undoc-members": True}
autodoc_member_order = 'bysource'

html_domain_indices = False
html_show_sourcelink = False
html_show_sphinx = False
