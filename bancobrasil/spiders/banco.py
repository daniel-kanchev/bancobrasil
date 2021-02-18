import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bancobrasil.items import Article


class BancoSpider(scrapy.Spider):
    name = 'banco'
    start_urls = ['https://www.bb.com.br/portalbb/page120,3366,3367,1,0,1,0.bb?codigoNoticia=0']

    def parse(self, response):
        links = response.xpath('//a[@class="linkChamada_5"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        if title == 'Veja Também':
           title = response.xpath('//div[@id="tituloSubHomeNoticia"]//p//text()').get()

        date = response.xpath('//div[@class="data"]/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d/%m/%y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//p[@class="margemB_10"]//text()').getall() or \
                  response.xpath('//div[@id="tituloSubHomeNoticia"]//p//text()').getall()

        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
