import scrapy
import csv
import logging

class ExampleSpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['caadf.org.br']
    start_urls = ['https://www.caadf.org.br/category/convenios/']
    f = open("oab/src/assets/descontos.json", 'w').close()

    def parse(self, response):
        # Encontrando links para as páginas de convênios
        convenio_links = response.css('.content .post-listing  .more-link::attr(href)').getall()
        pages = response.css('.pagination  a::attr(href)').getall()
        logging.warning(pages)

        for convenio_link in convenio_links:
            yield response.follow(convenio_link, callback=self.parse_convenio)

        for page in pages:
            yield response.follow(page, callback=self.parse)

    def parse_convenio(self, response):
        # Obtendo informações do convênio
        title = response.css('h1 span::text').get()
        date = response.css('.tie-date::text').get()
        cats = response.css('.post-cats a::text').getall()
        content = response.css('.entry').get()

        # Salvando informações em um arquivo CSV
        yield {
            'title': title,
            'date': date,
            'cats': cats,
            'content': content
        }