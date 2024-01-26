import requests
import os

# 此模块用于在天行数据上拉取童话故事

# key: a3f4b93c6a611f570c01d18354f70993
#  id: 352fe25daf686bdb
# GET: https://apis.tianapi.com/fairytales/index 

# 请求信息:
# Request Info:show
# Request Header:
# Content-Length: 55
# Content-Type: application/x-www-form-urlencoded

# 测试代码：
# # -*- coding: utf-8 -*-
# import http.client, urllib, json
# conn = http.client.HTTPSConnection('apis.tianapi.com')  #接口域名
# params = urllib.parse.urlencode({'key':'a3f4b93c6a611f570c01d18354f70993','id':'352fe25daf686bdb'})
# headers = {'Content-type':'application/x-www-form-urlencoded'}
# conn.request('POST','/fairytales/index',params,headers)
# tianapi = conn.getresponse()
# result = tianapi.read()
# data = result.decode('utf-8')
# dict_data = json.loads(data)
# print(dict_data)

# 创建一个爬虫类
# 首先，实例为蜘蛛，属性有名字，每一只蜘蛛会建立连接，解析数据，保存数据
class Spider(object):

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }

    # 配置请求,返回json数据
    def request(self):
        resp = requests.get(
            url=self.url,
            headers=self.headers,
            params={
                'key': '注册天行数据，获取一个key到这里'
            }
        )
        resp.encoding = 'utf-8'
        # 拿到标题
        #         content_json = resp.json()['newslist'][0]['title']
        #         拿到内容
        #         content_json = resp.json()['newslist'][0]['content']
        content_json = resp.json()

        return content_json

    #     保存数据
    def savetext(self, content, filename):
        f = open(filename, 'w')

        f.write(content + '\n')

        f.close()

        return 1


def main():
    url = 'http://api.tianapi.com/joke/index' # https://www.tianapi.com/article/195   http://api.tianapi.com/joke/index
    spider = Spider('笑话', url)

    # 每天抓十条数据
    contents = ''
    # 输出文案
    datajson = spider.request()
    for i in range(10):
        try:
            # 标题
            print(datajson)
            title = datajson['newslist'][i]['title']
            print(title)
            # 内容
            content = datajson['newslist'][i]['content']
            # 合并
            merge = ''
            merge = title + '\n' + content
            contents += '\n'
            contents += merge
        except Exception as e:
            print(e)

    #  保存到文件,成功返回1
    print(spider.savetext(contents, os.getcwd() + '/Crawler/downZip/joke.txt'))


if __name__ == '__main__':
    main()