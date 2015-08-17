"""
The common imports of this project, resolved against the right python version.

Ignore any errors about missing modules in here.
"""
PYTHON_MAJOR = __import__('sys').version_info[0]
py3 = PYTHON_MAJOR == 3

import util
bs4 = util.importlocal('bs4')
requests = util.importlocal('requests')
__all__ = ['requests', 'bs4', 'py3', 'PYTHON_MAJOR']
