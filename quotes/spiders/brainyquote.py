"""
> scrapy crawl brainyquote -o quotes.jl
"""

import json
from functools import partial
from scrapy import Spider, Request
from scrapy.exceptions import CloseSpider
from bs4 import BeautifulSoup

MAX_PAGES = 10

TOPICS = {
    'art': 't:132567',
    'life': 't:132584',
    'love': "t:132585",
    'success': 't:132597',
    'wisdom': 't:132601'
}
TOKENS = {
    'art': '472df6298178e7332dc3864fa0bc5321',
    'life': '407e2f46887fe58aca68f5dd3bda7b27',
    'love': "4f8d17ad65c6c6a72d2ef0d410c0a1d0",
    'success': '42ca14cae96f3f7cec1bd27f55d38919',
    'wisdom': 'cd93282b6e64d2227c381d99b8a962d2'
}


class BrainyquoteSpider(Spider):
    name = 'brainyquote'
    allowed_domains = ['brainyquote.com']
    start_urls = ['https://www.brainyquote.com']

    def parse(self, response):
        for quote in response.css('#quotesList div.boxy'):
            yield self.extract_html(quote)
        # Continue to API
        for topic in TOPICS:
            parse_topic = partial(self.parse_api, topic, 1)
            yield from parse_topic()

    def extract_html(self, q):
        text = q.css('.clearfix a.b-qt::text').extract_first().strip()
        tags = q.css('.kw-box a.oncl_list_kc::text').extract()
        author = q.css('.clearfix a.bq-aut::text').extract_first().strip()
        return {
            'text': text,
            'author': author,
            'tags': sorted(tags)
        }

    def parse_api(self, topic, page=1, response=None):
        if page > MAX_PAGES:
            return

        self.logger.info(f'--- API for {topic}, page {page} ---')

        if response:
            body = json.loads(response.body)['content']
            for quote in BeautifulSoup(body, 'lxml').find_all('div', class_='boxy'):
                yield self.extract_json(quote)

        h = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json;charset=UTF-8"
        }
        body = {'id': TOPICS[topic], 'langc': 'en', 'pg': page,
                'typ': 'topic', 'v': '8.5.7b:3079556', 'vid': TOKENS[topic]}

        # To next page!
        page += 1

        parse_topic = partial(self.parse_api, topic, page)
        yield Request("https://www.brainyquote.com/api/inf", callback=parse_topic,
                      method='POST', headers=h, body=json.dumps(body))

    def extract_json(self, q):
        try:
            text = q.find('a', class_='b-qt').text.strip()
            tags = [a.text for a in q.find_all('a', class_='oncl_list_kc')]
            author = q.find('a', class_='bq-aut').text.strip()
            return {
                'text': text,
                'author': author,
                'tags': sorted(tags)
            }
        except Exception:
            return
