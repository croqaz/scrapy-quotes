"""
> scrapy crawl goodreads -o quotes.jl -a tag=humor
> scrapy crawl goodreads -o quotes.jl -a pages=3
"""

import scrapy
from bs4 import BeautifulSoup
from .. import util

PAGES = 0
MAX_PAGES = 250  # The max is 100 anyway


class GoodreadsSpider(scrapy.Spider):
    name = 'goodreads'
    allowed_domains = ['goodreads.com']

    def start_requests(self):
        global MAX_PAGES
        url = 'https://www.goodreads.com/'
        tag = getattr(self, 'tag', None)
        author = getattr(self, 'author', None)
        if tag:
            url = url + 'quotes/tag/' + tag
        elif author:
            url = url + 'author/quotes/' + author
        else:
            url = url + 'quotes/'
        pages = getattr(self, 'pages', 0)
        try:
            pages = int(pages)
            if pages > 0:
                MAX_PAGES = int(pages)
        except Exception as err:
            self.logger.warning('Pages option error: %s', err)
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        global PAGES
        for quote in response.css('.quote .quoteDetails'):
            yield self.extract_one(quote)

        next_page = response.css('a.next_page::attr(href)').extract_first()
        if next_page:
            PAGES += 1
            if PAGES >= MAX_PAGES:
                return
            yield response.follow(next_page, callback=self.parse)

    def extract_one(self, q):
        # Cleaning the text is tricky
        soup = BeautifulSoup(q.css('.quoteText').extract_first(), 'lxml')
        [x.decompose() for x in soup.find_all('script')]
        [x.decompose() for x in soup.find_all(class_='authorOrTitle')]
        [br.replace_with('\n') for br in soup.find_all('br')]
        text = soup.div.text.strip().rstrip('―').strip()
        del soup
        # Fix and normalize text
        text = util.clean_text(text).replace('“', '').replace('”', '').strip()

        # The rest of the elements are not a problem
        author = q.css('.quoteText .authorOrTitle::text')\
            .extract_first().strip().rstrip(',')
        likes = q.css('.quoteFooter .right a::text')\
            .extract_first().split()[0]
        tags = q.css('.quoteFooter .left a::text').extract()
        data = {
            'text': text,
            'author': author,
            'likes': int(likes)
        }
        if tags:
            data['tags'] = tags
        return data
