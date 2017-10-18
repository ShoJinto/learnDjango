#!/usr/bin/env ptyon
# coding:utf-8
from urllib import request,parse
import json
import sys
from time import sleep

'''
通过分析lagou.com的网页可以比较容易的构造出被爬取网页的url、headers以及post的data信息。
使用curl构造一个post实例：curl -A 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3' -e 'https://www.lagou.com/jobs/ list_python?city=%E5%85%A8%E5%9B%BD&cl=false&fromSearch=true&labelWords=&suginput=' -d 'first=false&pn=5&kd=python' -XPOST "https://www.lagou.com/jobs/positionAjax.json? needAddtionalResult=false&isSchoolJob=0"
从curl实例中可以很容易看出post到服务器上的data字典各个字段的意思。
'''

url = r'https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false&isSchoolJob=0'

def get_page(url,page_num):
    headers = {
        'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
        'Referer': r'https://www.lagou.com/jobs/list_python?city=%E5%85%A8%E5%9B%BD&cl=false&fromSearch=true&labelWords=&suginput=',
        'Connection': 'keep-alive'
    }
    data = {
        'first':'true', #当前是否显示第一页默认true，如果你在网页上点击了翻页此选项将变成false
        'pn':page_num,  #页码编号
        'kd':'Python java'   #搜索关键字，可以填多个
    }
    
    data = parse.urlencode(data).encode('utf-8')
    req = request.Request(url,headers=headers)
    
    try:    
        page = request.urlopen(req,data=data).read()
        page = page.decode('utf-8')
    except error.HTTPError as e:
        print(e.code)
        print(e.read().decode('utf-8'))
    return page


for page_num in range(1,31):
    try:    
        result_Set = json.loads(get_page(url,page_num))
        company_list = result_Set['content']['positionResult']['result']
    except KeyError as e: #经过测试发现拉钩对数据请求的频率做了限制，一次只能爬取5页。此处做异常处理----延时60s再进行接着进行爬取
        for i in range(60):
            sys.stdout.write(str('#') * (0 + i) + '\r')
            sys.stdout.flush()
            sleep(1)
    
    for i in company_list:
        top_banner = '========Jobs From lagou.com========='
        data = '''职位名称：%s\n薪资：%s\n职位优势：%s\n工作年限：%s\n学历：%s\n地区：%s - %s
行业：%s\n公司名称：%s\n职位标签：%s\n公司性质：%s\n公司规模；%s\n发布时间：%s''' % (i['positionName'],i['salary'],i['positionAdvantage'], \
                                                    i['workYear'],i['education'],i['city'],i['district'],i['industryField'], \
                                                    i['companyFullName'],i['positionLables'],i['financeStage'],i['companySize'], \
                                                    i['formatCreateTime'])
        bot_banner = 'page %s' % page_num
        with open('job_list.txt', mode='a+',encoding='utf-8') as f:
            f.write('%s\n%s' % (top_banner,data))
            
    with open('job_list.txt', mode='a+', encoding='utf=8') as f:
        f.write('''
        %s''' % bot_banner)
     
    #显示进度条   
    sys.stdout.write(bot_banner + str('.') * (0 + page_num) + '\r')
    sys.stdout.flush()
    
    #页码计数器
    page_num += 1 



