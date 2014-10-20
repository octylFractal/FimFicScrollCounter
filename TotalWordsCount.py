# local libs
import autharea
import shelfmanager
from commonimports import request
from util import *

# some differnt data getters
TOTAL_WORDS_READ = "totalWords"
PARTIALLY_READ_STORIES = "partialStories"

def get_user_shelves(username, password):
    lib = []
    load_from_site = user_bool(input('Use all bookshelves on the site (y/n)? '))
    if load_from_site:
        return autharea.get_user_shelves(username, password)
    inp = ''
    while True:
        inp = input('Next bookshelf or return to finish\n%s: ' % lib)
        if inp.isdigit():
            lib.append(int(inp))
            print(lib)
        else:
            break
    return lib

def main(method=TOTAL_WORDS_READ, proxy='', bookshelves=[], username=None, password=None):
    try:
        if len(bookshelves) == 0:
            bookshelves = get_user_shelves(username, password)
        # setup login
        request.install_opener(get_opener(proxy))
        lenbook = len(bookshelves)
        print('Connected to FimFiction, analyzing ' + number_objects(lenbook, 'bookshel', F_VES_ENDINGS) + '.')
        for shelf in bookshelves:
            obj = shelfmanager.Shelf(int(shelf), username, password)
            wc = obj.get_wordcount()
            print(shelf, "=", wc)
        input('Press enter to exit')
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    except BaseException as e:
        # scope things
        def do_fail():
            debug = False
            try:
                fail('Error: ' + str(e).encode('ascii', errors='replace').decode('ascii'))
            except SystemExit:
                pass
            except AssertionError:
                debug = True
            return debug
        reraise = do_fail()
        if reraise and py3:
            raise
        elif reraise:
            raise

if __name__ == "__main__":
    main()
