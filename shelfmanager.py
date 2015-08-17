"""Literally everything to do with the actual processing and sorting"""
from util import get_page, get_url, deprettify, print, prettify, number_objects, FIMFICTION, LIST_VIEW
from commonimports import bs4

url_cache = {}

def get_story_data(story):
    """
    Get story data from fimfic:
    Returns a dict: {
        'name': name of story, 'story_wc': word count of story,
        'per_chapter_wc': list of word counts for each chapter,
        'chapter_wc_sum': sum of all chapter word counts (sum(get_story_data(story)['per_chapter_wc']))
    }
    story - url to story, assumed relative to FIMFICTION
    """
    if story not in url_cache:
        #print('Loading story data of', story)
        soup = bs4.BeautifulSoup(get_url(FIMFICTION + story), 'lxml')
        name = str(soup(class_="story_name")[0].string)
        chapters = soup(class_="word_count")
        story_wc = int(deprettify(chapters[-1].b.string))
        chapters = chapters[:-1]
        chapter_indiv_wc = [int(deprettify(x.get_text())) for x in chapters]
        chapter_wc_sum = sum(chapter_indiv_wc)
        if story_wc != chapter_wc_sum:
            print('WARNING: chapter word count ({}) did not match story word count ({}) for story {}'\
                  .format(story_wc, chapter_wc_sum, name))
        url_cache[story] = {
            'name': name, 'story_wc': story_wc, 'per_chapter_wc': chapter_indiv_wc, 'chapter_wc_sum': chapter_wc_sum
        }
        #print(story + "'s data:", url_cache[story])
    return url_cache[story]

class Shelf():
    def __init__(self, shelf_id, username='', password=''):
        self.shelf = shelf_id
        self.usr = username
        self.pas = password
        self.first_page = bs4.BeautifulSoup(get_page(self.shelf, 1, LIST_VIEW), 'lxml')
        self.story_count = None
        self.pages = None
        self.stories = None
        self.perchap_wc = None
        self.wordcount = None

    def get_wordcount(self):
        if self.wordcount is None:
            print('Fetching word count for', self.shelf)
            self.find_count()
            self.deter_page_count()
            self.load_stories()
            self.wordcount = sum(get_story_data(x)['story_wc'] for x in self.stories)
            print('Loaded word count for', self.shelf)
        return self.wordcount

    def get_wordcount_per_chapter(self):
        if self.perchap_wc is None:
            print('Fetching word count per chapter for', self.shelf)
            self.find_count()
            self.deter_page_count()
            self.load_stories()
            self.perchap_wc = {}
            for x in self.stories:
                data = get_story_data(x)
                self.perchap_wc[x] = data['per_chapter_wc']
            print('Loaded', len(self.perchap_wc), 'per-chapter word counts for', self.shelf)
        return self.perchap_wc

    def find_count(self):
        if self.story_count is None:
            print('Fetching story count for', self.shelf)
            soup = self.first_page
            count = soup(class_="search_results_count")[0]('b')[2].string
            self.story_count = int(count)
        return self.story_count

    def deter_page_count(self):
        if self.pages is None:
            print('Determing pages for', self.shelf)
            soup = self.first_page
            pages = soup(class_="page_list")[0].ul('li')
            if len(pages) < 2:
                # only one page
                last_page = 1
            else:
                last_page = pages[-2].string
            self.pages = int(last_page)
            print('Page count is', self.pages, 'for', self.shelf)
        return self.pages

    def load_stories(self):
        if self.stories is None:
            print('Loading story urls for', self.shelf)
            s = []
            for page in range(self.pages):
                print('Loading page', page, 'out of', self.pages, 'for', self.shelf)
                soup = self.first_page if page == 0 else bs4.BeautifulSoup(get_page(self.shelf, page + 1, LIST_VIEW), 'lxml')
                bold_tags = soup(class_="search_results_count")[0]('b')
                from_ = int(bold_tags[0].string)
                to = int(bold_tags[1].string)
                # there are 1-60 stories on the first page which means 60, but 60-1=59 so we add one
                count = (to - from_) + 1
                story_list = soup(class_="story-list")[0]('li')
                for story in story_list:
                    s.append(story(class_="right")[0].h2.a['href'])
            self.stories = tuple(s)
            print(number_objects(len(self.stories), 'url(|s)'), 'loaded for', self.shelf)
        return self.stories
