"""
> scrapy crawl brainyquote -o quotesBrainy.jl
"""

import json
from functools import partial
from scrapy import Spider, Request
from bs4 import BeautifulSoup

MAX_PAGES = 3

TOPICS = {
    'art': 't:132567',
    'beauty': 't:132608',
    'computers': 't:132570',
    'friendship': 't:132578',
    'good': 't:132656',
    'life': 't:132584',
    'love': 't:132585',
    'motivational': 't:132622',
    'success': 't:132597',
    'wisdom': 't:132601',
}
TOKENS = {
    'art': '472df6298178e7332dc3864fa0bc5321',
    'beauty': 'a772f4ac071559552cee0783b7495f83',
    'computers': '5b818fb79423ce78f16a5a5016b9b21b',
    'friendship': '30432fd35e5fac68154c017c589238dd',
    'good': '10765501cdb2ed919cca81ad29f1421f',
    'life': '407e2f46887fe58aca68f5dd3bda7b27',
    'love': '4f8d17ad65c6c6a72d2ef0d410c0a1d0',
    'motivational': '7b363d749b4c7c684ace871c8a75f8e6',
    'success': '42ca14cae96f3f7cec1bd27f55d38919',
    'wisdom': 'cd93282b6e64d2227c381d99b8a962d2',
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
            try:
                yield from parse_topic()
            except Exception:
                pass

    def extract_html(self, q):
        text = q.css('.clearfix a.b-qt::text').extract_first().strip()
        tags = q.css('.kw-box a.oncl_list_kc::text').extract()
        author = q.css('.clearfix a.bq-aut::text').extract_first().strip()
        return {
            'text': text,
            'author': author,
            'tags': sorted(tags),
        }

    def parse_api(self, topic, page=1, response=None):
        if MAX_PAGES > 0 and page > MAX_PAGES:
            return

        self.logger.info(f'--- API for {topic}, page {page} ---')

        if response:
            body = json.loads(response.body)['content']
            for quote in BeautifulSoup(body, 'lxml').find_all('div', class_='boxy'):
                yield self.extract_json(quote, topic)

        h = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json;charset=UTF-8"
        }
        body = {
            'id': TOPICS[topic],
            'langc': 'en',
            'pg': page,
            'typ': 'topic',
            'v': '8.6.0b:3084179',
            'vid': TOKENS[topic],
        }

        # To next page!
        page += 1

        parse_topic = partial(self.parse_api, topic, page)
        yield Request(
            "https://www.brainyquote.com/api/inf",
            callback=parse_topic,
            method='POST',
            headers=h,
            body=json.dumps(body))

    def extract_json(self, q, topic=None):
        try:
            text = q.find('a', class_='b-qt').text.strip()
            tags = [a.text.lower() for a in q.find_all('a', class_='oncl_list_kc')]
            tags.append(topic)
            author = q.find('a', class_='bq-aut').text.strip()
            return {
                'text': text,
                'author': author,
                'tags': sorted(tags),
            }
        except Exception:
            return
