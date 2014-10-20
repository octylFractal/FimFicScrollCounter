py3 = __import__('sys').version_info[0] > 2
import sys

# local libs
from commonimports import request, cookiejar
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
    sys.path.append('./py%slibs' % py2to3compat.PYTHON_VERSION_MAJOR)
    syspathmod = True
        

FIMFICTION = 'https://www.fimfiction.net'

def deprettify(numstr):
    return numstr.replace(',', '').strip()

def prettify(num):
    return "{:,}".format(num)

NONE_S_ENDINGS = ('', 's')
F_VES_ENDINGS = ('f', 'ves')
NONE_ES_ENDINGS = ('', 'es')

def number_objects(count, base, endings=NONE_S_ENDINGS):
    return str(count) + ' ' + (base + endings[0] if count == 1 else base + endings[1])

def fail(stri):
    print(stri)
    if input("Press enter to exit") == "debug" :
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
        res = str(conn.read()).replace(r'\t','') \
                   .replace('\r','') \
                   .replace('\n','') \
                   .replace(r'\r','') \
                   .replace(r'\n','') \
                   .replace('&#039;','\'') \
                   .replace('&amp;','&') \
                   .replace('&quot;','"')
        urlCache[url] = res
    return urlCache[url]

def get_page(shelf, pagenum):
    # pull page
    data = get_url(
        FIMFICTION + '/stories?order=date_added&completed=1&bookshelf={}&unread=1&page={}'.format(shelf, pagenum))
    return data

__import__('autharea')
__all__ = ['PrintAndFile', 'output', 'importlocal', 'FIMFICTION', 'number_objects',
           'F_VES_ENDINGS', 'NONE_ES_ENDINGS', 'NONE_S_ENDINGS', 'prettify', 'deprettify',
           'fail', 'get_opener', 'get_page', 'get_url', 'py3', 'opener', 'user_bool']
