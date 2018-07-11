# scrapy-examples
## Instruction
>1、用scrapy框架编写，抓取试卷及试题

>2、相关模块`BeautifulSoup4`、`Pillow`、`lxml`...

>3、图片下载，多管道处理

## Usage
>1、切换到工作目录

```
    cd zujuan
```

>2、运行spider

```
    spider crawl `spiderName`
```
## exercise.py
```
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

        if js["pager"]:
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
```
