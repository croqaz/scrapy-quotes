"""
> scrapy crawl azquotes -o quotes.jl -a tag=funny
"""

import scrapy

PAGES = 0
MAX_PAGES = 1


class AZquotesSpider(scrapy.Spider):
    name = 'azquotes'
    allowed_domains = ['azquotes.com']

    def start_requests(self):
        global MAX_PAGES
        tag = getattr(self, 'tag', None)
        author = getattr(self, 'author', None)
        if tag:
            url = f'https://www.azquotes.com/quotes/topics/{tag}.html'
        elif author:
            url = f'https://www.azquotes.com/author/{author}'
        else:
            url = 'https://www.azquotes.com/quote_of_the_day.html'

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
        for quote in response.css('.list-quotes .wrap-block'):
            yield self.extract_one(quote)

        next_page = response.css('.pager li.next a::attr(href)').get()
        if next_page:
            PAGES += 1
            if PAGES >= MAX_PAGES:
                return
            yield response.follow(next_page, callback=self.parse)

    def extract_one(self, q):
        text = q.css('a.title::text').get().strip()
        author = q.css('.author a::text').get().strip()
        likes = q.css('.share-icons a.heart24::text').get().strip()
        tags = [t.lower() for t in q.css('.mytags a::text').getall()]
        data = {
            'source': 'az',
            'text': text,
            'author': author,
        }
        if likes:
            data['likes'] = int(likes)
        if tags:
            data['tags'] = tags
        return data
