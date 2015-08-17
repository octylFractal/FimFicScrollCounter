"""
The common imports of this project, resolved against the right python version.

Ignore any errors about missing modules in here.
"""
PYTHON_MAJOR = __import__('sys').version_info[0]
py3 = PYTHON_MAJOR == 3
if py3:
    import urllib.parse as parse
    from http import cookiejar, cookies
    import urllib.request as request
else:
    import urllib as parse
    import cookielib as cookiejar
    import Cookie as cookies
    import urllib2 as request
import util

bs4 = util.importlocal('bs4')
__all__ = ['parse', 'cookiejar', 'cookies', 'request', 'bs4', 'py3', 'PYTHON_MAJOR']
