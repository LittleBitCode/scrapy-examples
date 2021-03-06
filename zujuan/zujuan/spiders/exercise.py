# -*- coding: utf-8 -*-
import re
import sys
import json
import time
import scrapy
import urlparse

from lxml            import html
from scrapy.http     import Request, FormRequest
from scrapy.selector import Selector

from zujuan.papers   import Paper
from zujuan.items    import ExerciseItem

reload(sys)
sys.setdefaultencoding("utf-8")

#CrawlSpider用来遍布抓取，通过rules来查找所有符合的URL来爬去信息
class ExerciseSpider(scrapy.Spider):  #抓取单一页面，没有rules
    name = 'zujuan'
    allowed_domains = ['zujuan.21cnjy.com/']
    start_urls = [
        'http://zujuan.21cnjy.com/paper/paper-exam-list?xd=3&chid=9&papertype=9&province_id=16&paperyear=2018'         #高中政治高考真题
    ]
    # 1:组卷网          :http://www.zujuan.com/
    # 2:橡皮网          :http://xiangpi.com/
    # 3:学科网(组卷)     :http://zujuan.xkw.com/
    # 4:菁优网          :http://www.jyeoo.com/
    # 5:小学学科网       :http://www.xuekeedu.com/
    # 6:21世纪教育网     :https://www.21cnjy.com/
    # 7:学科网           :http://zxxk.com/
    # 8:21组卷平台       :https://zujuan.21cnjy.com
    # 9:好教育云平台      :http://www.jtyhjy.com/
    #10:高考资源网        :https://www.ks5u.com/
    #11:学科王           :http://www.xuekewang.com/
    #12:中华资源库        :http://www.ziyuanku.com/
    #13:中学历史教学园地   :http://zujuan.zxls.com/
    site = '8'
    base_url = 'https://zujuan.21cnjy.com'
    xd = {
        '1' : "小学",
        '2' : '初中',
        '3' : '高中',
    }
    paper_type = {
        '9' : '高考模拟',
        '10': '高考真卷'
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
        js     = json.loads(response.body)
        lists  = js["list"]
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
                callback    = self.parse_exercise_list,
                meta        = {'paper': item},
                dont_filter = True
            )

        if js["pager"] != None:
            xml_string = html.fromstring(js["pager"])
            next_link  = xml_string.xpath("//div[@class='pagenum']/a[last()]/@href")[0]
            if next_link:
                yield Request(
                    url         = self.base_url + next_link,
                    callback    = self.parse,
                    dont_filter = True
                )

    # 分析试题列表
    def parse_exercise_list(self, response):
        js           = json.loads(response.body)
        lists        = js["content"]
        exercise_num = 0
        sort         = 0
        for list in lists:
            exercise_num += len(list['questions'])
            for question in list['questions']:
                sort += 1
                paper                        = response.meta['paper']
                exercise                     = ExerciseItem()
                exercise['subject']          = paper['subject']
                exercise['grade']            = paper['grade']
                exercise['site_id']          = self.site
                exercise['degree']           = self.degree[str(question['difficult_index'])]
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
                            exercise['options'] = json.dumps(the_options,ensure_ascii=False) # 不转码 存储到数据库为中文
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
                exercise['points']           = json.dumps(points,ensure_ascii=False) # 不转码 存储到数据库为中文
                exercise['url']              = self.base_url + '/question/detail/' + question['question_id']
                exercise['sort']             = unicode(sort)
                paper['exercise_num']        = exercise_num
                exercise['paper']            = paper
                exercise['description_imgs'] = description_imgs
                yield exercise
