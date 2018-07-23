# -*- coding: utf-8 -*-

import sys
import json
import time
import scrapy
import urlparse
from lxml            import html
from scrapy          import Request
from scrapy.selector import Selector
from zujuan.papers   import Paper
from zujuan.items    import ChapterItem
from zujuan.items    import SubjectItem
from zujuan.items    import ExerciseItem

reload(sys)
sys.setdefaultencoding("utf-8")

class ChapterExerciseSpider(scrapy.Spider):
    name = 'c_e'
    allowed_domains = ['zujuan.21cnjy.com']
    start_urls = [
        'https://zujuan.21cnjy.com/data/subjects',
        # 'https://zujuan.21cnjy.com/data/subjects',
        # 'https://zujuan.21cnjy.com/data/subjects-by-xd',
        # 'https://zujuan.21cnjy.com/catalog/cate-tree?xd=2&chid=2',
    ]
    site = '8'
    base_url = 'https://zujuan.21cnjy.com'
    term = '2'
    subject = '2'
    xd = {
        '1': "小学",
        '2': '初中',
        '3': '高中',
    }
    degree = {
        '1': '容易',
        '2': '较易',
        '3': '普通',
        '4': '较难',
        '5': '困难',
    }
    questionTypes = {
        '1': '单选题',
        '2': '多选题',
        '3': '判断题',
        '4': '填空题',
        '5': '计算题',
        '6': '解答题',
        '7': '完形填空',
        '8': '阅读理解',
        '9': '问答题',
        '10': '语言表达题',
        '11': '名著导读',
        '12': '句型转换',
        '13': '翻译',
        '14': '改错题',
        '15': '选词填空（词汇运用）',
        '16': '文言文阅读',
        '17': '现代文阅读',
        '18': '连词成句',
        '19': '默写',
        '20': '诗歌鉴赏',
        '21': '辨析题',
        '22': '补全对话',
        '23': '任务型阅读',
        '24': '单词拼写（词汇运用）',
        '25': '作图题',
        '26': '实验探究题',
        '27': '材料分析题',
        '28': '综合题',
        '30': '连线题',
        '31': '列举题',
        '32': '写作题',
        '34': '书写',
        '36': '应用题',
        '37': '选择题',
        '38': '双选题',
        '39': '听力题',
        '40': '语法填空',
        '41': '推断题',
    }
    chid = {
        '2': '语文',
        '3': '数学',
        '4': '英语',
        '5': '科学',
        '6': '物理',
        '7': '化学',
        '8': '历史',
        '9': '政治思品',
        '10': '地理',
        '11': '生物',
        '14': '信息技术',
        '15': '通用技术',
        '16': '劳技',
        '19': '基本能力',
        '20': '历史与社会',
        '21': '社会思品',
    }
    # 解析科目列表
    def parse(self, response):
        js_subjects = json.loads(response.body)
        for js_subject in dict(js_subjects).keys():
            subject             = SubjectItem()
            subject['id']       = str(js_subject)
            subject['name']     = js_subjects[js_subject]
            if subject['id'] == self.subject:
                yield Request(
                    self.base_url + '/catalog/cate-tree?xd=' + self.term + '&chid=' + self.subject,
                    callback    = self.parse_edition,
                    meta        = {'subject' : subject},
                    dont_filter = True,
                )
    # 解析版本信息
    def parse_edition(self, response):
        js_editions = json.loads(response.body)
        subject     = response.meta['subject']
        for js_edition in js_editions:
            if js_edition['title'] == '人教版（新课程标准）':
                yield Request(
                    self.base_url + '/catalog/cate-tree?xd=' + self.term + '&chid=' + self.subject + '&chapter_id=' + str(js_edition['id']),
                    callback    = self.parse_textbook,
                    meta        = {
                        'edition' : {
                            'id'      : js_edition['id'],
                            'name'    : js_edition['title'],
                        },
                        'subject' : subject
                    },
                    dont_filter = True,
                )

    #解析单元 章节
    def parse_textbook(self, response):
        editions = response.meta['edition']
        subject  = response.meta['subject']
        # 获取url参数列表
        result = urlparse.urlparse(response.url)
        params = urlparse.parse_qs(result.query)
        print(params['chapter_id'][0])
        js_textbooks = json.loads(response.body)
        for js_textbook in js_textbooks:
            grade = str(js_textbook['title']).split('年级')[0] + '年级'

            if js_textbook['title'] == '八年级上册':
                yield Request(
                    self.base_url + '/catalog/cate-tree?xd=' + self.term + '&chid=' + self.subject + '&chapter_id=' + str(js_textbook['id']),
                    callback    = self.parse_unit,
                    meta        = {
                        'textbook' : {
                            'id'         : js_textbook['id'],
                            'name'       : js_textbook['title'],
                            'site_id'    : self.site,
                            'edition'    : editions['name'],
                            'edition_id' : editions['id'],
                        },
                        'grade'   : grade,
                        'subject' : subject,
                    },
                    dont_filter = True,
                )

    # 解析单元
    def parse_unit(self,response):
        textbook = response.meta['textbook']
        subject  = response.meta['subject']
        grade    = response.meta['grade']
        # 解析返回结果
        js_units = json.loads(response.body)
        for js_unit in js_units:
            yield Request(
                self.base_url + '/catalog/cate-tree?xd=' + self.term + '&chid=' + self.subject + '&chapter_id=' + str(js_unit['id']),
                callback=self.parse_chapter,
                meta={
                    'textbook' : textbook,
                    'subject'  : subject,
                    'grade'    : grade,
                    'unit' : {
                        'id'         : js_unit['id'],
                        'site_id'    : self.site,
                        'name'       : js_unit['title'],
                        'edition'    : textbook['edition'],
                        'edition_id' : textbook['edition_id'],
                        'textbook'   : textbook['name'],
                        'textbook_id': textbook['id'],
                        'term'       : self.xd[self.term],
                        'subject'    : self.chid[self.subject],
                        'grade'      : grade,
                        'parent_id'  : '0',
                        'have_child' : js_unit['hasChild'],
                    }
                },
                dont_filter=True,
            )

    # 解析具体章节 无理数 有理数
    def parse_chapter(self, response):
        textbook = response.meta['textbook']
        subject  = response.meta['subject']
        grade    = response.meta['grade']
        unit     = response.meta['unit']
        # 解析返回结果
        js_chapters = json.loads(response.body)
        for js_chapter in js_chapters:
            if js_chapter['hasChild']:
                yield Request(
                    self.base_url + '/catalog/cate-tree?xd=' + self.term + '&chid=' + self.subject + '&chapter_id=' + str(js_chapter['id']),
                    callback=self.parse_chapter,
                    meta={
                        'textbook' : textbook,
                        'subject'  : subject,
                        'grade'    : grade,
                        'unit'     : {
                        'id'         : js_chapter['id'],
                        'site_id'    : self.site,
                        'name'       : js_chapter['title'],
                        'edition'    : textbook['edition'],
                        'edition_id' : textbook['edition_id'],
                        'textbook'   : textbook['name'],
                        'textbook_id': textbook['id'],
                        'term'       : self.xd[self.term],
                        'subject'    : self.chid[self.subject],
                        'grade'      : grade,
                        'parent_id'  : unit['id'],
                        'have_child' : js_chapter['hasChild'],
                    }
                    },
                    dont_filter=True,
                )
            else:
                yield Request(
                    self.base_url + '/paper/paper-category-list?xd=' + self.term + '&chid=' + self.subject + '&categories=' + str(js_chapter['id']),
                    callback=self.parse_paper,
                    meta={
                        'chapter': {
                            'id': js_chapter['id'],
                            'site_id': self.site,
                            'name': js_chapter['title'],
                            'edition': textbook['edition'],
                            'edition_id': textbook['edition_id'],
                            'textbook': textbook['name'],
                            'textbook_id': textbook['id'],
                            'term': self.xd[self.term],
                            'subject': self.chid[self.subject],
                            'grade': grade,
                            'parent_id': unit['id'],
                            'have_child': js_chapter['hasChild'],
                        },
                        'unit'     : unit,
                        'grade'    : grade,
                        'subject'  : subject,
                        'textbook' : textbook
                    },
                    dont_filter=True,
                )

    def parse_paper(self, response):
        subject  = response.meta['subject']
        chapter  = response.meta['chapter']
        grade    = response.meta['grade']
        unit     = response.meta['unit']
        # 获取url参数列表
        result = urlparse.urlparse(response.url)
        params = urlparse.parse_qs(result.query)
        # 解析返回结果
        js = json.loads(response.body)
        lists = js["list"]
        for list in lists:
            item                 = Paper()
            item['site_id']      = self.site
            item['title']        = list['title']
            item['grade']        = self.xd[params['xd'][0]]
            item['subject']      = self.chid[str(list['chid'])]
            item['type']         = list['typeName']
            item['level']        = list['paperlevel']
            item['views']        = list['look_num']
            item['year']         = list['paperyear']
            item['url']          = self.base_url + list['viewUrl']
            time_local           = time.localtime(int(list['addtime']))
            item['uploaded_at']  = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            yield Request(
                self.base_url + '/paper/detail?pid=' + list['pid'],
                callback    = self.parse_exercise,
                meta        = {
                    'paper'    : item,
                    'subject'  : subject,
                    'unit'     : unit,
                    'grade'    : grade,
                    'chapter'  : chapter
                },
                dont_filter = True
            )

        # if js["pager"] != None:
        #     xml_string = html.fromstring(js["pager"])
        #     next_link  = xml_string.xpath("//div[@class='pagenum']/a[last()]/@href")[0]
        #     if next_link:
        #         yield Request(
        #             url         = self.base_url + next_link,
        #             callback    = self.parse,
        #             dont_filter = True
        #         )

    # 解析试题
    def parse_exercise(self, response):
        subjects = response.meta['subject']  # 所有的科目
        chapter  = response.meta['chapter']
        paper    = response.meta['paper']
        grade    = response.meta['grade']
        unit     = response.meta['unit']
        # 获取url参数列表
        result = urlparse.urlparse(response.url)
        params = urlparse.parse_qs(result.query)
        # 解析返回结果
        js = json.loads(response.body)
        lists = js["content"]
        exercise_num = 0
        sort = 0
        for list in lists:
            exercise_num += len(list['questions'])
            for question in list['questions']:
                sort += 1
                paper = response.meta['paper']
                exercise = ExerciseItem()
                exercise['subject']     = paper['subject']
                exercise['grade']       = grade
                exercise['site_id']     = self.site
                exercise['degree']      = self.degree[str(question['difficult_index'])]
                exercise['source_id']   = question['question_id']
                exercise['type']        = self.questionTypes[str(question['question_channel_type'])]
                exercise['description'] = question['question_text']

                imgs = Selector(text=str(exercise['description'])).xpath('//img/@src').extract()
                description_imgs = {}
                if len(imgs) > 0:
                    for img in imgs:
                        img_url = img
                        description_imgs[img] = img_url
                options = question['options']
                if options != None or options == '':
                    if type(question['options']) == type({}):
                        the_options = []
                        allkeys = dict(question['options']).keys()
                        allkeys = sorted(allkeys)
                        if len(allkeys) > 0:
                            for key in allkeys:
                                the_options.append(options[key])
                            exercise['options'] = json.dumps(the_options, ensure_ascii=False)  # 不转码 存储到数据库为中文
                    else:
                        exercise['options'] = None
                else:
                    exercise['options'] = None
                exercise['answer']      = None
                exercise['answer_img']  = question['answer']
                exercise['method']      = None
                exercise['method_img']  = question['explanation']
                children = question['list']
                if children == None:
                    exercise['is_wrong'] = 0
                else:
                    if len(children) > 0:
                        exercise['is_wrong'] = 1
                    else:
                        exercise['is_wrong'] = 0
                all_points = question['t_knowledge']
                points = []
                if len(all_points) > 0:
                    for point in all_points:
                        if point != None:
                            points.append(str(point['name']))
                exercise['points']      = json.dumps(points, ensure_ascii=False)  # 不转码 存储到数据库为中文
                exercise['url']         = self.base_url + '/question/detail/' + question['question_id']
                exercise['sort']        = unicode(sort)
                paper['exercise_num']   = exercise_num
                exercise['paper'] = paper
                exercise['description_imgs'] = description_imgs
                exercise['section']          = {
                    'id': '2',
                    'name': '初中',
                }
                exercise['term']             = self.xd[self.term]
                exercise['unit']             = unit
                exercise['subjects']         = subjects
                exercise['chapter']          = chapter
                exercise['paper']            = paper
                yield exercise