# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ExerciseItem(scrapy.Item):
    type        = scrapy.Field()
    grade       = scrapy.Field()
    subject     = scrapy.Field()
    degree      = scrapy.Field()
    source_id   = scrapy.Field()
    paper_id    = scrapy.Field()
    description = scrapy.Field()
    options     = scrapy.Field()
    answer      = scrapy.Field()
    method      = scrapy.Field()
    points      = scrapy.Field()
    url         = scrapy.Field()
    sort        = scrapy.Field()
    paper       = scrapy.Field()

class ImageItem(scrapy.Item):
    image_urls  = scrapy.Field()
