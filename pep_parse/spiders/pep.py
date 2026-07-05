import re
from urllib.parse import urljoin

import scrapy

from pep_parse.items import PepParseItem


class PepSpider(scrapy.Spider):
    name = 'pep'
    allowed_domains = ['peps.python.org']
    start_urls = ['https://peps.python.org/']

    def parse(self, response):
        links = response.css(
            'table.pep-zero-table a[href^="pep-"]::attr(href)'
        ).getall()
        seen_urls = set()
        for link in links:
            pep_url = urljoin(response.url, link)
            if pep_url in seen_urls:
                continue
            seen_urls.add(pep_url)
            yield response.follow(pep_url, callback=self.parse_pep)

    def parse_pep(self, response):
        title = response.xpath('string(//h1[@class="page-title"])').get()
        title = title.strip() if title else None

        status_selector = (
            'dl.rfc2822.field-list.simple '
            'dt:contains("Status") + dd abbr::text'
        )
        status = response.css(status_selector).get()
        if status is None:
            status = response.css(
                'dl.rfc2822.field-list.simple dt:contains("Status") + dd::text'
            ).get()

        number = None
        pep_number_text = response.css(
            'dl.rfc2822.field-list.simple dt:contains("PEP") + dd::text'
        ).get()
        if pep_number_text and pep_number_text.strip().isdigit():
            number = int(pep_number_text.strip())

        if number is None:
            match = re.search(r'pep-(\d+)', response.url)
            if match:
                number = int(match.group(1))

        if number is None and title:
            match = re.search(r'PEP\s+(\d+)', title)
            if match:
                number = int(match.group(1))

        item = PepParseItem()
        item['number'] = number
        item['name'] = title
        item['status'] = status.strip() if status else None

        yield item
