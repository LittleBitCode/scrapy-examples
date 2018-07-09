# -*- coding: utf-8 -*-
import scrapy
import logging
import re
from w3lib.html import remove_tags
from lxml import html
from scrapy.http import Request, FormRequest, HtmlResponse
from scrapy.selector import Selector
import json
from zujuan.papers import Paper
from zujuan.items import ExerciseItem
import time
import urlparse

class ExerciseSpider(scrapy.Spider):
    name = 'zujuan'
    allowed_domains = ['zujuan.21cnjy.com/']
    start_urls = [
        'https://zujuan.21cnjy.com/',
        'https://zujuan.21cnjy.com/paper/view/',
        'https://zujuan.21cnjy.com/paper/paper-category-list?xd=2&chid=2',
        'https://zujuan.21cnjy.com/paper/paper-sync-list?xd=2&chid=2',
        'https://zujuan.21cnjy.com/paper/paper-exam-list?xd=2&chid=2'
    ]
    base_url = 'https://zujuan.21cnjy.com'
    xd = {
        '1' : "小学",
        '2' : '初中',
        '3' : '高中',
    }
    chid = {
        '2' : '语文',
        '3' : '数学',
        '4' : '英语',
        '5' : '科学',
        '6' : '物理',
        '7' : '化学',
        '8' : '历史',
        '9' : '政治思品',
        '10' : '地理',
        '11' : '生物',
        '14' : '信息技术',
        '15' : '通用技术',
        '16' : '劳技',
        '19' : '基本能力',
        '20' : '历史与社会',
        '21' : '社会思品',
    }
    grades = {
        '1' : '一年级',
        '2' : '二年级',
        '3' : '三年级',
        '4' : '四年级',
        '5' : '五年级',
        '6' : '六年级',
        '7' : '初一',
        '8' : '初二',
        '9' : '初三',
        '10': '高一',
        '11': '高二',
        '12': '高三',
        '13': '选修',
    }
    exam_types = {
        '1' : '小升初真题',
        '2' : '常考题',
        '7' : '模拟题',
    }
    unit = {
        '107565' : "第一单元",
        '107566' : "第二单元",
        '107567' : "第三单元",
        '107568' : "第四单元",
        '92833'  : "第五单元",
        '107570' : "第六单元",
    }
    #  publishing = {
    #     '10423' : "人教版（新课程标准）",
    #     '10424' : "苏教版",
    #     '10425' : "语文版",
    #     '10426' : "北师大版",
    #     '141760' : "部编版",
    # }
    questionTypes = {
        '1' : '单选题',
        '2' : '多选题',
        '3' : '判断题',
        '4' : '填空题',
        '5' : '计算题',
        '6' : '解答题',
        '7' : '完形填空',
        '8' : '阅读理解',
        '9' : '问答题',
        '10' : '语言表达题',
        '11' : '名著导读',
        '12' : '句型转换',
        '13' : '翻译',
        '14' : '改错题',
        '15' : '选词填空（词汇运用）',
        '16' : '文言文阅读',
        '17' : '现代文阅读',
        '18' : '连词成句',
        '19' : '默写',
        '20' : '诗歌鉴赏',
        '21' : '辨析题',
        '22' : '补全对话',
        '23' : '任务型阅读',
        '24' : '单词拼写（词汇运用）',
        '25' : '作图题',
        '26' : '实验探究题',
        '27' : '材料分析题',
        '28' : '综合题',
        '30' : '连线题',
        '31' : '列举题',
        '32' : '写作题',
        '34' : '书写',
        '36' : '应用题',
        '37' : '选择题',
        '38' : '双选题',
        '39' : '听力题',
        '40' : '语法填空',
        '41' : '推断题',
    }

    degree = {
        '1' : '容易',
        '2' : '较易',
        '3' : '普通',
        '4' : '较难',
        '5' : '困难',
    }
    post_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
        "Referer": "https://zujuan.21cnjy.com/",
    }

    # 分析试卷列表
    def parse(self ,response):
        #获取url参数列表
        result = urlparse.urlparse(response.url)
        params = urlparse.parse_qs(result.query)
        #解析返回结果
        js = json.loads(response.body)
        lists = js["list"]
        for list in lists:
            item = Paper()
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
                callback=self.parse_exercise_list,
                meta={'paper': item},
                dont_filter=True
            )

        if js["pager"]:
            xml_string = html.fromstring(js["pager"])
            next_link = xml_string.xpath("//div[@class='pagenum']/a[last()]/@href")[0]
            if next_link:
                yield Request(
                    url=self.base_url + next_link,
                    callback=self.parse,
                    dont_filter=True
                )

    # 分析试题列表
    def parse_exercise_list(self, response):
        js = json.loads(response.body)
        lists = js["content"]
        exercise_num = 0
        sort = 0
        for list in lists:
            exercise_num += len(list['questions'])
            for question in list['questions']:
                sort += 1
                paper                   = response.meta['paper']
                exercise                = ExerciseItem()
                exercise['subject']     = paper['subject']
                exercise['degree']      = self.degree[str(question['difficult_index'])]
                exercise['source_id']   = question['question_id']
                exercise['type']        = self.questionTypes[str(question['question_channel_type'])]
                exercise['description'] = question['question_text']
                exercise['options']     = json.dumps(question['options'])
                exercise['answer']      = question['answer']
                exercise['method']      = question['explanation']
                exercise['points']      = json.dumps(question['t_knowledge'])
                exercise['url']         = self.base_url + '/question/detail/' + question['question_id']
                exercise['sort']        = unicode(sort)
                paper['exercise_num']   = exercise_num
                exercise['paper']       = paper
                yield exercise
