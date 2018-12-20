"""
> scrapy crawl quoteworld -o quoteWorld.jl
"""
import re
import scrapy
from .. import util

MAX_PAGES = 3


class QuoteworldSpider(scrapy.Spider):
    name = 'quoteworld'
    allowed_domains = ['quoteworld.org']
    start_urls = ['http://www.quoteworld.org/browse/topic.html']

    def parse(self, response):
        # Check the path before diving in
        # In this case, the page contains the topics
        if response.url.endswith('browse/topic.html'):
            topics = response.xpath('//tr/td/a[contains(@href, "/browse_thetext_")]/@href').getall()
            for t in topics:
                yield response.follow(t)
        # This page contains quotes
        elif '/browse_thetext_' in response.url and response.url.endswith('.html'):
            page = response.meta.get('page', 0)
            if MAX_PAGES > 0 and page >= MAX_PAGES:
                return
            page += 1

            # Common tags for all the quotes on the page
            tags = response.xpath('//meta[@name="keywords"]/@content').extract_first()
            tags = (t for t in tags.split(',') \
                if t not in ('quote', 'quotation', 'famous') \
                and not (
                t.endswith('quote') or t.endswith('quotes') or t.endswith('quotation') or t.endswith('quotations')
            ))
            tags = sorted(set(tags))
            self.logger.info(f'--- Scanning tags {tags}, page {page} ---')

            for q in response.xpath('//tr/td[@width="516"][@valign="TOP"]'):
                text = q.css('b::text').extract_first().strip('"')
                text = util.clean_text(text)
                author = q.css('a.qlink::text').extract_first()
                author = re.sub(r' \(.+?\)', '', author).strip()
                yield {
                    'text': text,
                    'author': author,
                    'tags': tags,
                }
            # Is there a next page?
            try:
                next_page = response.css('tr td a.numbers::attr(href)')[-1].extract()
                if len(next_page) > len('.html'):
                    yield response.follow(next_page, callback=self.parse, meta={'page': page})
            except Exception:
                pass
