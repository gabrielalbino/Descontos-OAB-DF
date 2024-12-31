import logging
import scrapy
import re

class ConvenioSpider(scrapy.Spider):
    name = "convenio_spider"
    allowed_domains = ["caadf.org.br"]
    start_urls = ["https://www.caadf.org.br/category/convenios/"]

    custom_settings = {
        'LOG_LEVEL': 'INFO',  # Apenas logs INFO ou superiores
        'FEEDS': {
            'output/convenios.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 4,
            },
        },
    }

    def truncate_message(self, message, max_length=300):
        """Trunca mensagens longas."""
        if len(message) > max_length:
            return f"{message[:max_length]}... (mensagem truncada)"
        return message

    def parse(self, response):
        logging.info(self.truncate_message(f"Acessando: {response.url}"))
        links = response.css('.content .post-listing .more-link::attr(href)').getall()
        pages = response.css('.pagination a::attr(href)').getall()

        for link in links:
            yield response.follow(link, callback=self.parse_convenio)

        for page in pages:
            yield response.follow(page, callback=self.parse)

    def parse_convenio(self, response):
        logging.info(self.truncate_message(f"Extraindo convênio: {response.url}"))

        title = response.css('h1 span::text').get()
        date = response.css('.tie-date::text').get()
        cats = response.css('.post-cats a::text').getall()
        content = response.css('.entry').get()

        # Regex para capturar descontos
        discounts_regex = (
            r'<strong>Descontos?:?\s*</strong>(.*?)<\/p>|'  # Captura descontos simples
            r'Descontos?:?\s*(.*?)<\/p>|'  # Captura descontos simples sem <strong>
            r'(<p>\s*(I|II|III|IV|V|VI|VII|VIII|IX|X)[^<]*<br>.*?)<\/p>'  # Captura listas enumeradas
        )
        discounts = re.findall(discounts_regex, content, re.IGNORECASE | re.DOTALL)

        clean_discounts = []
        if discounts:
            for d in discounts:
                discount_text = d[0] or d[1] or d[2]
                if discount_text:
                    clean_discounts.append(re.sub(r'<[^>]*>', '', discount_text).strip())


        logging.info(f"Descontos: {clean_discounts}")

           # Remover HTML desnecessário e caracteres redundantes
        sanitized_content = re.sub(r'<(script|style|iframe|noscript)[^>]*>.*?</\1>', '', content, flags=re.DOTALL)
        sanitized_content = re.sub(r'<!--.*?-->', '', sanitized_content, flags=re.DOTALL)
        sanitized_content = re.sub(r'\t+', ' ', sanitized_content)
        sanitized_content = re.sub(r'\n+', ' ', sanitized_content)
        sanitized_content = re.sub(r'\s{2,}', ' ', sanitized_content).strip()
        sanitized_content = re.sub(r'<div class="clear">.*', '</div>', content, flags=re.DOTALL)

        #parse from brazilian date format to sortable date
        sortable_date = None
        if date:
            date_parts = date.split("/")
            if len(date_parts) == 3:
                sortable_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
                
        
        #remove all inline styles from content, to avoid conflicts with frontend styles
        regex = r'style="[^"]*"'
        content = re.sub(regex, '', content)
    
        item = {
            "title": (title or "").strip(),
            "date": (sortable_date or "").strip(),
            "cats": ", ".join(c.strip() for c in cats if c.strip() not in ["Convênios", "Destaques"]) if cats else "",
            "content": (sanitized_content or "").strip(),
            "discounts": ", ".join(clean_discounts) if clean_discounts else "",
            
        }

        yield item

    def closed(self, reason):
        logging.info(self.truncate_message(f"Spider finalizado. Motivo: {reason}"))