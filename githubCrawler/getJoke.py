# -*- coding: utf-8 -*-
import requests
import os

# 此模块用于在天行数据上拉取童话故事

# key: a3f4b93c6a611f570c01d18354f70993
#  id: 352fe25daf686bdb
# GET: https://apis.tianapi.com/fairytales/index 

# 测试代码：
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

    def __init__(self, name, url, key, id):
        self.name = name
        self.url = url
        self.key = key
        self.id = id
        # self.title = None
        # self.content = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
        }

    # 配置请求,返回json数据
    def request(self):
        resp = requests.post(
            url=self.url,
            headers=self.headers,
            params = {
                'key': self.key,
                'id' : self.id 
            }
        )
        resp.encoding = 'utf-8'
        content_json = resp.json()
        # # 拿到标题
        # self.title = content_json['result']['title']
        # # 拿到内容
        # self.content = content_json['result']['content']
        return content_json

    #     保存数据
    def savetext(self, content, filename):
        f = open(filename, 'w')

        f.write(content + '\n')

        f.close()

        return 1


def main():
    url = 'https://apis.tianapi.com/fairytales/index' # http://api.tianapi.com//fairytales/index   http://api.tianapi.com/joke/index
    key = 'a3f4b93c6a611f570c01d18354f70993',
    id = '352fe25daf686bdb'
    spider = Spider('笑话', url, key, id)

    # 每天抓1条数据
    contents = ''
    # 输出文案
    datajson = spider.request()

    for i in range(1):
        try:
            # 拿到标题
            title = datajson['result']['title']
            # 拿到内容
            content = datajson['result']['content']
            # 合并
            merge = ''
            merge = title + '\n' + content
            contents += '\n'
            contents += merge
        except Exception as e:
            print(e)

    #  保存到文件,成功返回1
    print(spider.savetext(contents, os.getcwd() + '/Crawler/downZip/fairytales.txt'))


    # 2.推送到公众号
    # 要传的草稿
    data = {
        "articles": [
            {
                "title": "关注【Python和数据分析】公众号",
                "author": "翔宇",
                "content": contents,
                "thumb_media_id": "这里需要用接口工具上传一张图片到公众号素材里，返回的mediaid放到这里，不懂请关注公众号“Python和数据分析“问作者"
            }
        ]
    }
    token_and_time = get_wxCode_token()
    access_token = token_and_time[0]
    getTokenTime = token_and_time[1]
    # 创建草稿实例
    caogao = Caogao('caogao',data,access_token,getTokenTime)
    caogao.send_requests()


if __name__ == '__main__':
    main()