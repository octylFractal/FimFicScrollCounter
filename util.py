import sys
import re

# local libs
autharea = None  # installed by autharea


class PrintAndFile():
    def __init__(self, target):
        self.target = target
        self.file = None
        self.oldprint = print

    def print(self, *message, sep=' ', end='\n', file=None, flush=False):
        self.oldprint(*message, sep=sep, end=end, file=file, flush=flush)
        self.oldprint(*message, sep=sep, end=end, file=self.file, flush=True)

    def close(self):
        self.file.close()

    def open(self):
        self.file = open(self.target, 'w+')


output = PrintAndFile('readlist.txt')
print = output.print

syspathmod = False


def add_local_import_path():
    global syspathmod
    if syspathmod:
        return
    sys.path.insert(0, './py%slibs' % sys.version_info[0])
    syspathmod = True


add_local_import_path()


def importlocal(name):
    """
    Import the given module.
    Acts pretty much like __import__(name),
    but the local py<major version>libs folder is added to the path
    """
    return __import__(name)


try:
    import requests
except ImportError:
    requests = importlocal('requests')

FIMFICTION = 'https://www.fimfiction.net'


def deprettify(numstr):
    return numstr.replace(',', '') \
        .replace(r'\t', '') \
        .replace('\r', '') \
        .replace('\n', '') \
        .replace(r'\r', '') \
        .replace(r'\n', '') \
        .strip(' \t\n\r')


def prettify(num):
    return "{:,}".format(num)


pluralpat = re.compile(r'(.*)\((.*)\|(.*)\)')
__pluralpatcache = dict()


def number_objects(count, wordstyle):
    if wordstyle not in __pluralpatcache:
        match = pluralpat.match(wordstyle)
        if not match:
            raise ValueError("wordstyle must be in style: base(singular|plural)")
        __pluralpatcache[wordstyle] = match
    match = __pluralpatcache[wordstyle]
    base = match.group(1)
    return str(count) + ' ' + (base + match.group(2) if abs(count) == 1 else base + match.group(3))


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


_session = None


def get_session(proxy=None) -> requests.Session:
    global _session
    if _session is None:
        _session = requests.Session()
        if proxy:
            _session.proxies = {'http': proxy}
            print('Using proxy: ' + proxy)
        _session.cookies['view_mature'] = 'true'
    return _session


# cache for multiple runs in one go
_url_cache = {}


def reset_cache():
    _url_cache.clear()


def get_url(url):
    if url not in _url_cache.keys():
        request = requests.get(url)
        _url_cache[url] = request.text
    return _url_cache[url]


FULL_VIEW = 0
LIST_VIEW = 1
CARD_VIEW = 2


def get_page(shelf, pagenum, view=LIST_VIEW):
    # pull page
    data = get_url(
        FIMFICTION +
        '/bookshelf/{}/?order=date_added&page={}&compact_view={}'
        .format(shelf, pagenum, view))
    return data


__import__('autharea')
__all__ = ['PrintAndFile', 'output', 'importlocal', 'FIMFICTION', 'number_objects',
           'prettify', 'deprettify', 'fail', 'get_session', 'get_page', 'get_url',
           'print', 'py3', 'user_bool', 'FULL_VIEW', 'LIST_VIEW',
           'CARD_VIEW']
