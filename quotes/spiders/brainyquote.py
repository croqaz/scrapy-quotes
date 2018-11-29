"""
> scrapy crawl brainyquote -o quotes.jl
"""

import scrapy


class BrainyquoteSpider(scrapy.Spider):
    name = 'brainyquote'
    allowed_domains = ['brainyquote.com']
    start_urls = ['https://www.brainyquote.com']

    def parse(self, response):
        for quote in response.css('#quotesList div.boxy'):
            yield self.extract_one(quote)

        # TODO
        # next_page = response.css('a.next_page::attr(href)').extract_first()
        # if next_page:
        #     yield response.follow(next_page, callback=self.parse)

    def extract_one(self, q):
        text = q.css('.clearfix a.b-qt::text').extract_first().strip()
        tags = q.css('.kw-box a.oncl_list_kc::text').extract()
        author = q.css('.clearfix a.bq-aut::text').extract_first().strip()
        return {
            'text': text,
            'author': author,
            'tags': sorted(tags)
        }
