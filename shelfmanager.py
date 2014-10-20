"""Literally everything to do with the actual processing and sorting"""
from util import get_url, FIMFICTION
from commonimports import bs4

def get_word_count(story):
    pass
    
class Shelf():
    def __init__(this, shelf_id, username='', password=''):
        this.shelf = shelf_id
        this.usr = username
        this.pas = password
        this.lazySoup = LazySoup(get_url(FIMFICTION + '/bookshelf/%s' % shelf_id))
        this.story_count = None
        this.pages = None
        this.stories = None
        this.wordcount = None

    def get_wordcount(this):
        if this.wordcount is None:
            return this.wordcount
        this.find_count()
        this.deter_page_count()
        this.load_stories()
        this.wordcount = sum(map(get_word_count, this.stories))
        return this.wordcount

    def find_count(this):
        soup = this.lazySoup.lazyCreateSoup()
        count = soup(class_="search_results_count")[0]('b')[2]
        print(count)
        pass

    def deter_page_count(this):
        pass

    def load_stories(this):
        pass

class LazySoup():
    def __init__(this, *args, **kwargs):
        this.args = args
        this.kwargs = kwargs
        this.soup = None

    def lazyCreateSoup(this):
        if not this.soup:
            this.soup = bs4.BeautifulSoup(*this.args, **this.kwargs)
        return this.soup
        
