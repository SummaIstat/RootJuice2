# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Rootjuice2Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    pa_id = scrapy.Field()
    url = scrapy.Field()
    titolo = scrapy.Field()
    scrapedText = scrapy.Field()
    depth = scrapy.Field()
    fonte = scrapy.Field()
    isBinary = scrapy.Field()
    indexingDate = scrapy.Field()
    lastModified = scrapy.Field()
