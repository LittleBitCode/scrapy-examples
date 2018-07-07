import scrapy

class Paper(scrapy.Item):
    title        = scrapy.Field()
    grade        = scrapy.Field()
    subject      = scrapy.Field()
    year         = scrapy.Field()
    type         = scrapy.Field()
    url          = scrapy.Field()
    level        = scrapy.Field()
    exercise_num = scrapy.Field()
    views        = scrapy.Field()
    uploaded_at  = scrapy.Field()