# -*- coding: utf-8 -*-

import sys
import json
import scrapy
import urlparse
from lxml            import html
from scrapy          import Request
from scrapy.selector import Selector
from zujuan.items    import EditionItem
from zujuan.items    import ExerciseItem
from zujuan.items    import TextBookItem

reload(sys)
sys.setdefaultencoding("utf-8")

class ChapterExerciseSpider(scrapy.Spider):
    name = 'c_e'
    allowed_domains = ['zujuan.21cnjy.com']
    start_urls = [
        # 'http://zujuan.21cnjy.com/'
        'https://zujuan.21cnjy.com/catalog/cate-tree?xd=2&chid=2',
        # 'https://zujuan.21cnjy.com/question/list?xd=2&chid=2&categories=107564&sort_field=time&filterquestion=0&page=1'
    ]
    site = '8'
    base_url = 'https://zujuan.21cnjy.com'
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
    # 获取版本信息
    def parse(self, response):
        js_editions = json.loads(response.body)
        for js_edition in js_editions:
            edition             = EditionItem()
            edition['id']       = js_edition['id']
            edition['title']    = js_edition['title']
            edition['hasChild'] = js_edition['hasChild']
            yield Request(
                self.base_url + '/catalog/cate-tree?xd=2&chid=2&chapter_id=' + str(js_edition['id']),
                callback    = self.parse_textbook,
                meta        = edition,
                dont_filter = True,
            )

    #获取单元
    def parse_textbook(self, response):
        js_textbooks = json.loads(response.body)
        for js_textbook in js_textbooks:
            textbook             = TextBookItem()
            textbook['id']       = js_textbook['id']
            textbook['title']    = js_textbook['title']
            textbook['hasChild'] = js_textbook['hasChild']
            yield Request(
                self.base_url + '/question/list?xd=2&chid=2&categories=' + str(textbook['id']),
                callback    = self.parse_exercise,
                meta        = textbook,
                dont_filter = True,
            )

    def parse_exercise(self, response):
        # 获取url参数列表
        result = urlparse.urlparse(response.url)
        params = urlparse.parse_qs(result.query)
        # 解析返回结果
        js = json.loads(response.body)
        questions = js["questions"]
        sort = 0
        for question in questions:
            sort += 1
            exercise                     = ExerciseItem()
            exercise['subject']          = self.chid[question['chid']]
            exercise['grade']            = self.xd[question['xd']]
            exercise['site_id']          = self.site
            exercise['degree']           = self.degree[str(question['difficult_index'])]
            exercise['paper_id']        = question['paperid']
            exercise['source_id']        = question['question_id']
            exercise['type']             = self.questionTypes[str(question['question_channel_type'])]
            exercise['description']      = question['question_text']

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
                        exercise['options'] = json.dumps(the_options,ensure_ascii=False)
                else:
                    exercise['options']  = None
            else:
                exercise['options']      = None
            exercise['answer']           = None
            exercise['answer_img']       = question['answer']
            exercise['method']           = None
            exercise['method_img']       = question['explanation']
            children                     = question['list']
            if children == None:
                exercise['is_wrong'] = 0
            else:
                if len(children) > 0:
                    exercise['is_wrong'] = 1
                else:
                    exercise['is_wrong'] = 0
            all_points                   = question['t_knowledge']
            points                       = []
            if len(all_points) > 0:
                for point in all_points:
                    if point != None:
                        points.append(str(point['name']))
            exercise['points']           = json.dumps(points,ensure_ascii=False)
            exercise['url']              = self.base_url + '/question/detail/' + question['question_id']
            exercise['sort']             = unicode(sort)
            exercise['description_imgs'] = description_imgs
            # print(exercise)
            # return
            yield exercise

        if js["pager"] != None:
            xml_string = html.fromstring(js["pager"])
            next_link  = xml_string.xpath("//div[@class='pagenum']/a[last()]/@href")[0]
            if next_link:
                yield Request(
                    url         = self.base_url + next_link,
                    callback    = self.parse_exercise,
                    dont_filter = True
                )