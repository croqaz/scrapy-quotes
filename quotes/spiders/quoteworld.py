
import re
import scrapy


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
            # Common tags for all the quotes on the page
            tags = response.xpath('//meta[@name="keywords"]/@content').extract_first()
            tags = [t for t in tags.split(',') if t not in ('quote', 'quotation', 'famous')]
            tags = [t for t in tags if not t.endswith('quote') and not t.endswith('quotation')]

            for q in response.xpath('//tr/td[@width="516"][@valign="TOP"]'):
                text = q.css('b::text').extract_first().strip('"')
                author = q.css('a.qlink::text').extract_first()
                author = re.sub(r' \(.+?\)', '', author).strip()
                yield {
                    'text': text,
                    'author': author,
                    'tags': tags
                }
            # Is there a next page?
            try:
                next_page = response.css('tr td a.numbers::attr(href)')[-1].extract()
                if len(next_page) > len('.html'):
                    yield response.follow(next_page, callback=self.parse)
            except Exception:
                pass
