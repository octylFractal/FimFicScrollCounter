"""Literally everything to do with the actual processing and sorting"""
from util import get_page, get_url, deprettify, prettify, number_objects, FIMFICTION, LIST_VIEW
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
    def __init__(this, shelf_id, username='', password=''):
        this.shelf = shelf_id
        this.usr = username
        this.pas = password
        this.first_page = bs4.BeautifulSoup(get_page(this.shelf, 1, LIST_VIEW), 'lxml')
        this.story_count = None
        this.pages = None
        this.stories = None
        this.perchap_wc = None
        this.wordcount = None

    def get_wordcount(this):
        if this.wordcount is None:
            print('Fetching word count for', this.shelf)
            this.find_count()
            this.deter_page_count()
            this.load_stories()
            this.wordcount = sum(get_story_data(x)['story_wc'] for x in this.stories)
            print('Loaded word count for', this.shelf)
        return this.wordcount

    def get_wordcount_per_chapter(this):
        if this.perchap_wc is None:
            print('Fetching word count per chapter for', this.shelf)
            this.find_count()
            this.deter_page_count()
            this.load_stories()
            this.perchap_wc = {}
            for x in this.stories:
                data = get_story_data(x)
                this.perchap_wc[x] = data['per_chapter_wc']
            print('Loaded', len(this.perchap_wc), 'per-chapter word counts for', this.shelf)
        return this.perchap_wc

    def find_count(this):
        if this.story_count is None:
            print('Fetching story count for', this.shelf)
            soup = this.first_page
            count = soup(class_="search_results_count")[0]('b')[2].string
            this.story_count = int(count)
        return this.story_count

    def deter_page_count(this):
        if this.pages is None:
            print('Determing pages for', this.shelf)
            soup = this.first_page
            pages = soup(class_="page_list")[0].ul('li')
            if len(pages) < 2:
                # only one page
                last_page = 1
            else:
                last_page = pages[-2].string
            this.pages = int(last_page)
            print('Page count is', this.pages, 'for', this.shelf)
        return this.pages

    def load_stories(this):
        if this.stories is None:
            print('Loading story urls for', this.shelf)
            s = []
            for page in range(this.pages):
                print('Loading page', page, 'out of', this.pages, 'for', this.shelf)
                soup = this.first_page if page == 0 else bs4.BeautifulSoup(get_page(this.shelf, page + 1, LIST_VIEW), 'lxml')
                bold_tags = soup(class_="search_results_count")[0]('b')
                from_ = int(bold_tags[0].string)
                to = int(bold_tags[1].string)
                # there are 1-60 stories on the first page which means 60, but 60-1=59 so we add one
                count = (to - from_) + 1
                story_list = soup(class_="story-list")[0]('li')
                for story in story_list:
                    s.append(story(class_="right")[0].h2.a['href'])
            this.stories = tuple(s)
            print(number_objects(len(this.stories), 'url(|s)'), 'loaded for', this.shelf)
        return this.stories
