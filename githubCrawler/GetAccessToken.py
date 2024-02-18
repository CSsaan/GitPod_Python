#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : deepboat
# @Desc    : 连接网络 获取 access_token
# @Date    : 2023/11/17 17:41
import json
import random
import os

import requests
import time
import toml


class Basic:
    def __init__(self, conf_file):
        self.firstTime = True
        self.confFile = conf_file
        self.confInfo = self.read_toml()
        self.appID = self.confInfo["basic"]["app_id"]
        self.appSecret = self.confInfo["basic"]["app_secret"]
        self.accessToken = self.confInfo["basic"]["access_token"]
        self.tokenTime = self.confInfo["basic"]["token_time"]
        self.userAgent = self.get_user_agent()

    def read_toml(self):
        conf_file = toml.load(self.confFile)
        return conf_file

    def write_toml(self):
        self.confInfo["basic"]["app_id"] = self.appID
        self.confInfo["basic"]["app_secret"] = self.appSecret
        self.confInfo["basic"]["access_token"] = self.accessToken
        self.confInfo["basic"]["token_time"] = self.tokenTime
        with open(self.confFile, "w", encoding="utf-8") as f:
            toml.dump(self.confInfo, f)

    # // 获取token
    def get_wechat_token(self):
        # 判断token是否过期
        if self.which_token_over():

            try:
                params = {
                    "grant_type": "client_credential",
                    "appid": self.appID,
                    "secret": self.appSecret
                }
                headers = {'User-Agent': self.userAgent}
                post_url = "https://api.weixin.qq.com/cgi-bin/token"
                response_post = requests.post(url=post_url, params=params, headers=headers)
                print(response_post)
                print(response_post.text)
                res = json.loads(response_post.text)
                access_token = res["access_token"]

                self.accessToken = access_token
                self.tokenTime = time.time()
                self.write_toml()
                return self.accessToken
            except Exception as e:
                print(e)
                return False
        else:
            return self.accessToken

    # 判断token是否过期
    def which_token_over(self):
        # 确保第一次可获取
        if(self.firstTime):
            self.firstTime = False
            return True
        # 获取当前时间戳 -- 时间戳是自1970年1月1日午夜以来的秒数
        now_time = time.time()
        # 用当前时间戳减去getTokenTime，大于两个小时就判定失效
        hour2 = 2 * 60 * 60
        if now_time - self.tokenTime > hour2:
            return True
        return False

    def get_user_agent(self):
        user_agent = random.choice(self.confInfo["web"]["user_agents"])
        return user_agent


if __name__ == '__main__':
    my_basic = Basic(os.getcwd() + "/Crawler/utils/conf.toml")
    my_basic.get_wechat_token()

