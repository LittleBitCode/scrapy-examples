# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item,Field

class ExerciseItem(Item):
    type             = Field()
    grade            = Field()
    subject          = Field()
    degree           = Field()
    source_id        = Field()
    paper_id         = Field()
    site_id          = Field()
    description      = Field()
    options          = Field()
    answer           = Field()
    answer_img       = Field()
    method           = Field()
    method_img       = Field()
    points           = Field()
    url              = Field()
    sort             = Field()
    paper            = Field()
    is_wrong         = Field()
    section          = Field()
    subject          = Field()
    editon           = Field()
    textbook         = Field()
    unit             = Field()
    term             = Field()
    chapter          = Field()
    parent_id        = Field()
    subjects         = Field()
    description_imgs = Field()


class ImageItem(Item):
    image_urls       = Field()

# 科目
class SubjectItem(Item):
    id               = Field()
    name             = Field()
    site_id          = Field()
    section_id       = Field()

# 版本信息
class EditionItem(Item):
    id               = Field()
    name             = Field()
    site_id          = Field()
    subject_id       = Field()
    section_id       = Field()

class TextBookItem(Item):
    id               = Field()
    name             = Field()
    term             = Field()
    grade            = Field()
    subject          = Field()
    edition          = Field()
    site_id          = Field()
    source_id        = Field()
    edition_id       = Field()


class ChapterItem(Item):
    id               = Field()
    source_id        = Field()
    edition_id       = Field()
    edition          = Field()
    textbook_id      = Field()
    textbook         = Field()
    name             = Field()
    parent_id        = Field()
    subject          = Field()
    grade            = Field()
    have_child       = Field()
    site_id          = Field()