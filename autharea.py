import sys
import re

# local libs
from util import FIMFICTION, get_url, get_session, fail_or_e
from commonimports import bs4

usr = ''
pas = ''
logged_in = False


def possibly_req_auth(username, password):
    global usr, pas, logged_in
    if logged_in:
        return
    if not usr:
        usr = username or input('Username: ')
    if not pas:
        pas = password or input('Password: ')
    ret = get_session().post(FIMFICTION + '/ajax/login', data={'username': usr, 'password': pas})
    try:
        data = ret.json()
        if 'signing_key' not in data:
            raise AssertionError()
    except BaseException as e:
        fail_or_e('Login failed, check your username and password', e)
    logged_in = True
    return usr, pas


patterns = {'bookshelfid': re.compile(r'/bookshelf/(\d+)/.+')}


def get_user_shelves(username, password):
    username, password = possibly_req_auth(username, password)
    library = get_url(FIMFICTION + ('/user/{}/library'.format(username)))
    libsoup = bs4.BeautifulSoup(library, 'lxml')
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
