import sys
import re

# local libs
autharea = None  # installed by autharea

class PrintAndFile():
    def __init__(this, file):
        this.file = file

    def println(this, message):
        this.file.write(message + '\n')
        print(message)

    def close(this):
        this.file.close()
output = PrintAndFile(open('readlist.txt', 'w'))

syspathmod = False
importtable = {}
def importlocal(name):
    """
    Import the given module.
    Acts pretty much like __import__(name),
    but the local py<major version>libs folder is added to the path
    """
    if not name in importtable:
        add_local_import_path(name)
        importtable[name] = __import__(name)
    return importtable[name]

def add_local_import_path(name):
    global syspathmod
    if syspathmod:
        return
    sys.path.append('./py%slibs' % sys.version_info[0])
    syspathmod = True

# down here because cyclic deps
from commonimports import request, cookiejar


FIMFICTION = 'https://www.fimfiction.net'

def deprettify(numstr):
    return numstr.replace(','  , '') \
                 .replace(r'\t', '') \
                 .replace('\r' , '') \
                 .replace('\n' , '') \
                 .replace(r'\r', '') \
                 .replace(r'\n', '') \
                 .strip(' \t\n\r')

def prettify(num):
    return "{:,}".format(num)

pluralpat = re.compile(r'(.*)\((.*)\|(.*)\)')
def number_objects(count, wordstyle):
    match = pluralpat.match(wordstyle)
    if not match:
        raise ValueError("wordstyle must be in style: base(singular|plural)")
    base = match.group(1)
    return str(count) + ' ' + (base + match.group(2) if count == 1 else base + match.group(3))

def fail(stri):
    print(stri)
    if input("Press enter to exit") == "debug":
        raise AssertionError(stri)
    sys.exit()

def user_bool(inp):
    """Convert inp to bool: False unless 'y' or 'yes' or 'true' or '1'"""
    inp = inp.lower()
    result = False
    if inp == 'y' or inp == 'yes' or inp == 'true' or inp == '1':
        result = True
    return result

opener = None
def get_opener(proxy=''):
    global opener
    if not opener is None:
        return opener
    if proxy != '':
        opener = request.build_opener(
                              request.ProxyHandler({'http':proxy}),
                              request.HTTPBasicAuthHandler(),
                              request.HTTPHandler,
                              request.HTTPCookieProcessor(cookiejar.CookieJar()))
        print('Using proxy: ' + proxy)
    else:
        opener = request.build_opener(
                              request.HTTPBasicAuthHandler(),
                              request.HTTPHandler,
                              request.HTTPCookieProcessor(cookiejar.CookieJar()))
    return opener

# cache for multiple runs in one go
urlCache = {}
def reset_cache():
    urlCache.clear()

def get_url(url):
    if not url in urlCache.keys():
        req = request.Request(url)
        req.add_header('Cookie', autharea.design_cookie('view_mature=true'))
        conn = request.urlopen(req)
        res = str(conn.read())
        urlCache[url] = res
    return urlCache[url]

FULL_VIEW = 0
LIST_VIEW = 1
CARD_VIEW = 2

def get_page(shelf, pagenum, view=LIST_VIEW):
    # pull page
    data = get_url(
        FIMFICTION +\
        '/bookshelf/{}/?order=date_added&page={}&compact_view={}'\
        .format(shelf, pagenum, view))
    return data

__import__('autharea')
__all__ = ['PrintAndFile', 'output', 'importlocal', 'FIMFICTION', 'number_objects',
           'prettify', 'deprettify', 'fail', 'get_opener', 'get_page', 'get_url',
           'py3', 'opener', 'user_bool', 'FULL_VIEW', 'LIST_VIEW', 'CARD_VIEW']
