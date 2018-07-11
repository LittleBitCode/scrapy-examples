# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item,Field

class ExerciseItem(Item):
    type        = Field()
    grade       = Field()
    subject     = Field()
    degree      = Field()
    source_id   = Field()
    paper_id    = Field()
    description = Field()
    options     = Field()
    answer      = Field()
    method      = Field()
    points      = Field()
    url         = Field()
    sort        = Field()
    paper       = Field()

class ImageItem(Item):
    image_urls  = Field()
