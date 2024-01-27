# 此模块作用：将文本内容上传到公众号草稿箱，可参考https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html
# 全流程：
# 步骤：1.获取access_token
#      2.从天行数据拉去想要的文本数据并解析整理
#      3.调用上传草稿的接口使用post方式上传文本数据

# 步骤：
# 1.拿到token,用一个变量来记录获取token时的时间戳，每次执行时先检查时间达到2个小时的才去获取token
token = ''
getTokenTime = 0


class Caogao(object):

    def __init__(self,name,data,access_token,getTokenTime):
        self.name = name
        self.data = data
        self.access_token = access_token
        self.getTokenTime = getTokenTime

    # 先判断是否有token，如果没有，获取token，同时记录时间，获取后开始干活儿，
    # 如果有，判断是否失效，失效则重新获取，
    # 判断token是否过期
    def which_token_abate(self):
        # 获取token时间戳
        # global getTokenTime
        # 获取当前时间戳
        nowtime_stamp = time.time()
        # 用当前时间戳减去getTokenTime，大于两个小时就判定失效
        hour2 = 2 * 60 * 60 * 1000
        if nowtime_stamp - self.getTokenTime > hour2:
            return True
        return False

    # 判断是否有token
    def have_token(self):
        if self.access_token != '':
            return True
        return False

    # 发送数据，data为要发的内容
    def send_requests(self):
        # 2.导入requests包,发送post
        try:
            header_dict = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
                'Content-Type': 'application/json; charset=utf-8'
            }
            response_psot = requests.post(
                url='https://api.weixin.qq.com/cgi-bin/draft/add?',
                params={
                    'access_token': self.access_token},
                headers=header_dict,
                data=bytes(json.dumps(self.data, ensure_ascii=False).encode('utf-8'))
                # data=self.data,
            )

            print(response_psot)
        except Exception as e:
            print(e)


def main():
    # 1.抓取笑话数据
    url = 'http://api.tianapi.com/joke/index'
    spider = Spider('笑话', url)

    # 每天抓十条数据
    contents = ''
    # 建立请求
    datajson = spider.request()
    # 解析数据
    for i in range(11):
        try:
            # 标题
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
    # print(spider.savetext(contents, 'joke.txt'))

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
    for _ in range(10):
        main()