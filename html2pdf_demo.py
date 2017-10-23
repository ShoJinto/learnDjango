#!/usr/bin/env python
# encoding:utf-8

import os
import pdfkit
from urllib import request
from bs4 import BeautifulSoup
from venv import __main__

base_url =r'http://www.cnblogs.com/pick'
html_head='''
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<link href="http://www.cnblogs.com/bundles/blog-common.css?v=ChDk9h03-S75WEqNhGvXkWireJ5cCWdK1xRM9NIXfnM1" rel="stylesheet" type="text/css"/>
</head>
'''
headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Connection':   'keep-alive'
}

def get_page_count():
    page_count=get_pages(base_url, headers).find(name='a', attrs={'class':'last'})
    return int(page_count.string)

def get_pages(base_url,headers):
    '''
    base_url:
    headers:
    return:beautifulsoup object
    '''
    req = request.Request(base_url,headers=headers)
    page = request.urlopen(req).read()
    page = page.decode('utf-8')
    soup = BeautifulSoup(page,"lxml")
    return soup

#获取每一篇博客的url并保存到一个以名字为key、url为value的字典中
def get_blog_urls(soup):
    blog_urls={}
    post_urls = soup.find_all(name='a',attrs={'class':'titlelnk'})

    url_num = 0
    for i in post_urls:
        blog_urls[i.string]=i['href']
        url_num += 1
        print('get blog curls (%d/%d)' % (url_num, len(post_urls)))
    return blog_urls

#获取每一篇文章的内容并将其保存到一个以名字为key内容为value的字典中
def get_content_for_each_page():
    posts={}
    blog_total=len(get_blog_urls(get_pages(base_url, headers)))
    page_num = 0
    for blog_name,blog_url in get_blog_urls(get_pages(base_url, headers)).items():
        post_title=get_pages(blog_url, headers).find(name='h1', attrs={'class':'postTitle'})
        post_content=get_pages(blog_url, headers).find_all(name='div', attrs={'id':'cnblogs_post_body'})[0]
        posts[blog_name]=html_head+str(post_title)+str(post_content)
        page_num += 1
        print('get blog contents (%d/%d)' % (page_num, blog_total))
    return posts      

def save_to_pdf(pdf_dir):
    for name,content in get_content_for_each_page().items():
        print('\033[31msaving %s\033[0m' % name)
        pdfkit.from_string(content, ('%s/%s.pdf' % (pdf_dir,name)), options={'encoding':'utf-8'})
        print('\033[31mdone %s\033[0m' % name)

#获取目录中pdf文件的个数
def get_file_count():
    pdf_file_count=0
    for _,_,files in os.walk(dir_name):
        for file in files:
            if os.path.splitext(file)[1]=='.pdf':
                pdf_file_count += 1
    return pdf_file_count
    
if __main__:
    dir_name=os.getcwd()+'/pdfs'
    pdf_file_count = get_file_count()
    
    #判断保存pdf的目录是否存在
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    
    '''
    循环爬取cnblogs的精华文章直到没有精华文章可以爬取为止。
    get_page_count 获取精华文章总页数
    get_pages 获取每篇文章的具体页面
    get_blog_urls 获取每篇文章的url地址和文章的标题并保存为一个字典
    get_content_for_each_page 获取文章内容以及标题保存到一个字典中
    save_to_pdf 遍历字典的内容并将其保存成pdf存放到本地指定位置
    '''
    #翻页计数器  
    if pdf_file_count >=20:
        start_pn=int(pdf_file_count/20) #需要爬取的blogs的页码采用取整的方式如果上次爬取到某个也没的第19篇文章，那么这次需要从该页面的第一篇文章开始爬取
        for pn in range(start_pn+1,get_page_count()+1):
            base_url='%s/%s/' % (r'http://www.cnblogs.com/pick',pn)
            save_to_pdf(dir_name) 
            print('pn (%d/%d)' % (start_pn+1,get_page_count()))
    else:
        #将爬取到的内容保存成pdf文档
        save_to_pdf(dir_name) 




