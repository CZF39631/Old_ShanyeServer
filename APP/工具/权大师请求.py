import os

import requests
import json
import time
import random
import pandas as pd
from collections import defaultdict

# 清除环境变量中的代理设置
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('no_proxy', None)
os.environ.pop('NO_PROXY', None)

# 确保 no_proxy 环境变量存在，即使它为空
os.environ['no_proxy'] = '*'


def 生成时间戳():
    当前时间戳 = str(int(time.time() * 1000))
    随机数 = str(random.randint(1, 10000))
    return 当前时间戳 + 随机数


def 生成签名():
    当前时间戳 = str(int(time.time() * 1000))
    随机数 = str(random.randint(1, 10000))
    return 当前时间戳 + 随机数


def 搜索品牌信息(查询关键词):
    url = 'https://phoenix.quandashi.com/brandSearch/webBrandSearch'
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://so.quandashi.com",
        "priority": "u=1, i",
        "referer": "https://so.quandashi.com/",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }

    签名 = 生成签名()
    时间戳 = 生成时间戳()

    数据 = {
        "v": "1.0",
        "executor": "657346644261474651504474574458723748664d74513d3d",
        "sign": 签名,
        "appKey": "quandashi4380977532",
        "partnerId": "1000",
        "signMethod": "md5",
        "timestamp": 时间戳,
        "userIde": "657346644261474651504474574458723748664d74513d3d",
        "platform": 1,
        "q": 查询关键词,
        "brandRule": "1",
        "申请人筛选": "",
        "申请人地址筛选": "",
        "代理机构筛选": "",
        "advanceFilter": "",
        "intCls": "",
        "countryName": "",
        "createYear": "",
        "statusName": "",
        "userName": "qds9287150",
        "typeCode": "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45",
        "page": 0,
        "style": "",
        "pageSize": 20,
        "sort": "",
        "商标筛选": "",
        "searchKey": "",
        "groupFilter": "",
        "标源": 0,
        "评审文书": 0,
        "serviceGoods": "",
        "param": 5,
        "field": "data_id",
        "检索报告": "1_返回近似数据_10"
    }
    数据 = json.dumps(数据, separators=(',', ':'))

    响应 = requests.post(url, headers=headers, data=数据)

    if 响应.status_code == 200:
        结果 = 响应.json()
        if 结果.get('code') == 8888:  # 验证码提示
            print("请验证！程序暂停。")
            input("按任意键继续...")
            return None  # 返回None以指示需要重试
        return 结果
    else:
        print(f"请求失败，状态码：{响应.status_code}")
        return None


def 获取品牌服务项目(申请号):
    url = 'https://phoenix.quandashi.com/brand/查询一批申请号的商品服务项目'
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://so.quandashi.com",
        "priority": "u=1, i",
        "referer": "https://so.quandashi.com/",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
    }
    签名 = 生成签名()
    时间戳 = 生成时间戳()
    数据 = {
        "v": "1.0",
        "executor": "657346644261474651504474574458723748664d74513d3d",
        "sign": 签名,
        "appKey": 'quandashi4380977532',
        "partnerId": "1000",
        "signMethod": "md5",
        "timestamp": 时间戳,
        "userIde": "657346644261474651504474574458723748664d74513d3d",
        "platform": 1,
        "申请号列表": 申请号
    }
    数据 = json.dumps(数据, separators=(',', ':'))

    响应 = requests.post(url, headers=headers, data=数据)
    if 响应.status_code == 200:
        # 保存响应到指定路径
        return 响应.text
    else:
        print(f"请求失败，状态码：{响应.status_code}")
        return None


def 分类小类(响应数据):
    响应数据 = json.loads(响应数据)
    # 确保响应数据是字典类型
    if not isinstance(响应数据, dict):
        raise ValueError("传入的参数必须是字典类型")

    结果 = ""
    在用小类 = {}
    已删除小类 = {}
    # 遍历数据并分类
    for 类别, 项目列表 in 响应数据.get("data", {}).items():



        for 项目 in 项目列表:
            if 项目["isDelete"] == "0":
                if 项目["code"] not in 在用小类:
                    在用小类[项目["code"]] = []
                在用小类[项目["code"]].append(项目["name"])
            elif 项目["isDelete"] == "2":
                if 项目["code"] not in 已删除小类:
                    已删除小类[项目["code"]] = []
                已删除小类[项目["code"]].append(项目["name"])

        # 格式化输出
        结果 = "、".join([f"{code}：{', '.join(names)}" for code, names in 在用小类.items()])

    return 结果


def 处理信息(项目):
    信息 = 项目.get('data', {}).get('items', {})[0]
    申请号 = 信息.get('regNo')
    申请人 = 信息.get('applicantCn')
    商标名称 = 信息.get('tmName')
    商标图链接 = 信息.get('tmLogoUrl')
    品类 = 信息.get('intCls')
    申请号_大类 = str(申请号) + '_' + str(品类)
    服务项目 = 获取品牌服务项目(申请号_大类)
    服务类别 = 分类小类(服务项目)
    return {
        "商标名": 商标名称,
        "申请号": 申请号_大类,
        "申请人": 申请人,
        "商标图链接": 商标图链接,
        "未删除小类": 服务类别,
        "备案平台": ""
    }


def 查询关键词(关键词):
    项目 = 搜索品牌信息(关键词)
    商标信息 = 处理信息(项目)
    return 商标信息




if __name__ == '__main__':
    关键词 = '76795987'
    查询关键词(关键词)
