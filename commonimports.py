"""
The common imports of this project, resolved against the right python version.

Ignore any errors about missing modules in here.
"""
import util
if util.py3:
    import urllib.parse as parse
    from http import cookiejar, cookies
    import urllib.request
else:
    import urllib as parse
    import cookielib as cookiejar
    import Cookie as cookies
    import urllib2 as request
bs4 = util.importlocal('bs4')
__all__ = ['parse', 'cookiejar', 'cookies', 'request', 'bs4']
