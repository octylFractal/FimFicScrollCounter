import py2to3compat
py2to3compat.fix(__builtins__)
if py2to3compat.PYTHON_VERSION_MAJOR > 2:
    # uses new name
    import urllib.parse as parse
    from http import cookiejar, cookies
    from urllib.request import *
else:
    import urllib as parse
    # uses py3 name
    import cookielib as cookiejar
    # uses py3 name
    import Cookie as cookies
    from urllib2 import *

localCookie = ''

def designCookie(additionalCookies=[]):
    cookie = ''
    if localCookie:
        cookie = localCookie
    for add in additionalCookies:
        if cookie:
            cookie += '; ' + add
        else:
            cookie = add
    return cookie

def get_user_shelves(username, password):
    authRes = ''
