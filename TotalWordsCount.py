# local libs
import autharea
import shelfmanager
import util
from util import get_session, number_objects, user_bool, fail, print

# some differnt data getters
TOTAL_WORDS = "total_words"
WORDS_READ_BY_STORY_READ = "read_by_story"
WORDS_READ_BY_CHAPTER_READ = "read_by_chapter"
ALL = [TOTAL_WORDS, WORDS_READ_BY_CHAPTER_READ, WORDS_READ_BY_STORY_READ]


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


def total_words(allshelves: list):
    words = 0
    for s in allshelves:
        words += s.get_wordcount()
    print('Total words for', allshelves, '=', words)


def read_by_story(allshelves):
    print('By Story NYI')


def read_by_chapter(allshelves):
    print('By Chapter NYI')


def main(method='', proxy=None, bookshelves=[], username=None, password=None):
    util.output.open()
    try:
        # activate proxy
        get_session(proxy)
        bookshelves = bookshelves or get_user_shelves(username, password)
        method = method or input('Choose an analyzer ' +
                                 str(ALL)
                                 .replace('[', '(')
                                 .replace(']', ')')
                                 .replace("'", "") +
                                 ': ')
        # setup login
        lenbook = len(bookshelves)
        print('Connected to FimFiction, analyzing ' + number_objects(lenbook, 'bookshel(f|ves)') + '.')
        shelves = []
        for shelf in bookshelves:
            obj = shelfmanager.Shelf(int(shelf), username, password)
            shelves.append(obj)
        # call the appropriate method
        globals()[method](shelves)
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
        if reraise:
            raise
    finally:
        util.output.close()


if __name__ == "__main__":
    main()
