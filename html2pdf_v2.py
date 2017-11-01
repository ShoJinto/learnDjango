#!/urs/bin/env python
# coding:utf-8
#
'''
对爬取cnblogs.com上的文章并保存为本地pdf文档进行优化，
1.最开始采用requests模块进网页爬取，因为前一个版本使用的的是urllib,这个版本才用一种新的模块。
2.在爬取的时候发现爬取的某一篇文章呈现布局和浏览器中呈现的不一样
3.查找原因，结果是该html中嵌套了javascript代码，直接爬取的html代码当然和浏览器解析过不一样
4.这个问题其实也很简单找一个能够解析html中嵌套js代码的“非传统浏览器”即可，经过一番goole之后发现还真用这样的浏览器（方式）
5.PhantomJS与chrome headless的抉择，经过自己反复测试，确定选用chrome headless，为什么不用PhantomJS呢？
因为我发现经过PhantomJS解析之后所获得html代码任然和requests获取到的一模一样，结果是然并卵。因此选择了chrome headless
6.参考连接：https://segmentfault.com/a/1190000009399609#articleHeader1
7.浏览器关键字： chrome headless PhantomJS selenium
'''

import os
from time import sleep
# import requests
import progressbar

from lxml import etree
from selenium import webdriver

import pdfkit

base_url = r'http://www.cnblogs.com/pick'
html_head = '''
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<link href="http://www.cnblogs.com/bundles/blog-common.css?v=ChDk9h03-S75WEqNhGvXkWireJ5cCWdK1xRM9NIXfnM1" rel="stylesheet" type="text/css"/>
</head>
'''
headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Connection': 'keep-alive',
}

bar = progressbar.ProgressBar(
    widgets=[
        '[ ', progressbar.SimpleProgress(), ' ]',
        progressbar.Bar(),
        '[', progressbar.AnimatedMarker(), ']',
        progressbar.AbsoluteETA()
    ]
)

pdfkit_options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'custom-header': [
        ('Accept-Encoding', 'gzip')
    ],
    'cookie': [
        ('cookie-name1', 'cookie-value1'),
        ('cookie-name2', 'cookie-value2'),
    ],
    'quiet': '',
    'no-outline': None
}

pdfkit_config = pdfkit.configuration(
    wkhtmltopdf=r'D:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

blog_list = dict()  # 定义一个字典变量，用于保存博客名称对应的博客连接
blogs = dict()  # 定义一个字典变量，用于保存博客名称对应的博客内容

# defiend browser using chrome or phantomjs
# browser = webdriver.PhantomJS(executable_path='F:\\jtxiao\\program\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

browser = webdriver.Chrome(chrome_options=chrome_options,
                           executable_path="F:\\jtxiao\\program\chromedriver.exe")


# res = requests.get(base_url,headers=headers)
browser.get(base_url)
res = browser.page_source
page = etree.HTML(res)

total_page = int([i.text for i in page.xpath(
    '//div[@class="pager"]/a[last()-1]')][0])

blog_name = [name.text for name in page.xpath(
    '//div[@class="post_item_body"]/h3/a[@class="titlelnk"]')]
blog_url = page.xpath('//div[@class="post_item_body"]/h3/a/@href')

for i in bar(range(len(blog_name))):
    blog_list[blog_name[i]] = blog_url[i]

for name, url in blog_list.items():
    #     content_res = requests.get(url,headers=headers,params={'coding':'utf-8'}).text
    browser.get(url)
    content_res = browser.page_source
    blog_content_page = etree.HTML(content_res)
    browser.quit()

#     soup = BeautifulSoup(content_res.text,'lxml')
#     blog_content = soup.select('div#cnblogs_post_body')

    blog_title = blog_content_page.xpath('//h1[@class="postTitle"]')[0]
    blog_content = blog_content_page.xpath('//div[@id="cnblogs_post_body"]')[0]
#     blog_contentblog_title = blog_content_page.xpath('//div[@id="topics"]/*')

    blogs[name] = html_head + etree.tostring(blog_title, encoding='unicode') + \
        etree.tostring(blog_content, encoding='unicode')

    try:
        pdfkit.from_string(
            blogs[name],
            str(name) + '.pdf',
            options=pdfkit_options,
            configuration=pdfkit_config
        )

    except OSError as er:
        print('OSError:{0}'.format(er))

    break
