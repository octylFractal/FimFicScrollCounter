import sys
import re

# local libs
from commonimports import parse
from util import importlocal, FIMFICTION, get_url, get_opener, fail
bs4 = importlocal('bs4')

localCookie = ''
usr = ''
pas = ''
logged_in = False

def possibly_req_auth(username, password):
    global usr, pas, logged_in, localCookie
    if logged_in:
        return
    if not usr:
        if not username: username = input('Username: ')
        usr = username
    if not pas:
        if not password: password = input('Password: ')
        pas = password
    login_data = parse.urlencode(
        {'username': usr,'password': pas}
        ).encode('ascii')
    ret = get_opener().open(FIMFICTION + '/ajax/login.php', login_data)
    if str(ret.read()).find('0') == -1: 
        fail('Login failed, check your username and password')
    logged_in = True
    localCookie = ret.info()['Set-Cookie']
    return (usr, pas)

def design_cookie(additional_cookies=[]):
    if type(additional_cookies) is str:
        additional_cookies = [x.strip() for x in additional_cookies.split(";")]
    cookie = ''
    if localCookie:
        cookie = localCookie
    for add in additional_cookies:
        if cookie:
            cookie += '; ' + add
        else:
            cookie = add
    return cookie

patterns = {'bookshelfid': re.compile(r'/bookshelf/(\d+)/.+')}

def get_user_shelves(username, password):
    (username, password) = possibly_req_auth(username, password)
    library = get_url(FIMFICTION + ('/user/{}/library'.format(username)))
    libsoup = bs4.BeautifulSoup(library)
    shlvs = libsoup(class_='bookshelf-card')
    lib = []
    for shlf in shlvs:
        count = int(shlf('a')[0].b.string)
        if count != 0:
            link = str(shlf('a')[0]['href'])
            match = patterns['bookshelfid'].match(link)
            lib.append(int(match.group(1)))
    return lib

__import__('util').autharea = sys.modules[__name__]
