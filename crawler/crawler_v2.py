#!/usr/bin/env python
#

# import requests
import pdfkit
from bs4 import BeautifulSoup
import os
from selenium import webdriver

import progressbar

startUrl = r'https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000'
rootUrl = r'https://www.liaoxuefeng.com'
headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Host': r'www.liaoxuefeng.com',
    'Referer': startUrl,
    'Connection': 'keep-alive',
}

pdfkit_options = {
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'header-line': '',
    'header-font-size': 6,
    'header-right': "作者：廖雪峰",
    'footer-line': '',
    'footer-font-size': 6,
    'footer-right': "PDF制作：JTXIAO",
    'footer-center': "[page] / [topage]",
    'custom-header': [
        ('Accept-Encoding', 'gzip')
    ],
    'cookie': [
        ('cookie-name1', 'cookie-value1'),
        ('cookie-name2', 'cookie-value2'),
    ],
    'quiet': '',
    'load-error-handling': 'ignore',
    # 'no-outline': None
}

pdfkit_config = pdfkit.configuration(
    wkhtmltopdf=r'D:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

bar = progressbar.ProgressBar(
    widgets=[
        '[ ', progressbar.SimpleProgress(), ' ]',
        progressbar.Bar(),
        '[', progressbar.AnimatedMarker(), ']',
        progressbar.AbsoluteETA()
    ]
)

# browser = webdriver.PhantomJS(executable_path='F:\\jtxiao\\program\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe')

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

browser = webdriver.Chrome(chrome_options=chrome_options,
                           executable_path="F:\\jtxiao\\program\chromedriver.exe")

# client = requests.Session()


def getCharpterUrl(url, headers=headers):
    '''
    获取教程目录的url,并返回一个以章节名称为key对应url为value的字典
    '''
    urls = {}
    # html = client.get(url, headers=headers).text
    browser.get(url)
    html = browser.page_source
    # with open('pdfs/nav.html', 'r', encoding='utf-8') as f:  #为调试方便，可以第一次运行脚本的时候将网页源码保存到本地，以减少网络请求带来的时间消耗或被服务端refuse
    #     html = f.read()
    soup = BeautifulSoup(html, 'lxml')

    indexTree = soup.find(
        name='ul', attrs={'class': 'uk-nav uk-nav-side', 'id': 'x-wiki-index'})

    '''直接获取教程每个章节的url，不对章节的层次进行判断'''
    # urlData = indexTree.find_all(name='a')
    # for item in urlData:
    #     title = item.get_text()
    #     url = rootUrl + item['href']
    #     urls[title] = urls

    '''按照章节的层次对章节url进行获取'''
    navData = indexTree.find_all('div')
    for item in navData:
        depth = item.attrs['depth']  # 获取目录层级
        title = item.find('a').get_text()
        url = rootUrl + item.find(name='a').attrs['href']
        urls[title] = '!'.join([url, depth])  # 将目录层级与url用‘!’作为分隔符一并返回以备后面使用

    return urls


def parserArticle(title, starturl, headers=headers):
    '''
    解析html内容,并将内容作为结果返回
    '''
    url = starturl.split('!')[0]  # 获取每篇教程的真实url
    depth = starturl.split('!')[1]  # 获取该篇教程在整个教程中的目录层级
    browser.get(url)
    html = browser.page_source
    # browser.close()

    try:
        # html = client.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        content = soup.find(
            name='div', attrs={'class': 'x-wiki-content x-main-content'})

        '''
        爬取回来的html源码中img标签的src属性不正确，
        经过分析src和data-src的属性值是相同。
        此处进行调整一遍pdf中能正常显示图片
        '''
        for imgTag in soup.find_all(name='img', attrs={'src': 'https://cdn.webxueyuan.com/cdn/static/themes/default/img/loading.gif'}):
            imgTag['src'] = imgTag['data-src']

        '''
        将vidoe标签更换成a标签，一遍在pdf中有更好的阅读体验。
        a标签指向视频的网络地址，在阅读pdf的时候可以点击链接跳转到浏览器中观看视频
        '''
        for videoTag in soup.find_all('video'):
            videoLink = videoTag.find('source')['src']
            videoTag.name = 'a'
            videoTag.string = '点击链接观看'
            videoTag['target'] = '_blank'
            videoTag['href'] = videoLink

        '''
        按照原始网页进行处理，仅仅添加一个居中显示的内容标题
        '''
        # titleTag = soup.new_tag('h1')
        # titleTag.string = title  # 这是内容的标题名称
        # titleTag['align'] = 'center'  # h1标签居中属性
        # content.insert(0, titleTag)  # 将h1标签插入整个内容的最前面

        '''调整章节内容中的标题表情，以适用于wkthml2pdf对转换'''
        for hTag in content.find_all('h1'):
            hTag.name = 'strong'
            hTag['style'] = 'font-size:30px'
            hTag.name = 'strong'
            hTag['style'] = 'font-size:30px'

        for hTag in content.find_all('h3'):
            hTag.name = 'strong'
            hTag['style'] = 'font-size:20px'

        '''
        小标题前面添加4个br进行换行处理
        为每个章节添加一个居中显示的标题,使用h*标签的目的是让wkhtml2pdf能够生成清晰的树形目录结构.
        strong标签可以让每个章节的标题字体看起来一样大.
        通过观察目录的顶层depth值为0，下一级的depth值为1，再往下depth值增加1.因此可以使用
        `titleTagName = ''.join(['h',str(int(depth)+1)])`
        来构造h*标签
        '''
        for i in range(8):
            brTag = soup.new_tag('br')
            content.insert(0, brTag)

        titleTagName = ''.join(['h', str(int(depth) + 1)])
        titleTag = soup.new_tag(titleTagName)
        titleTag['align'] = 'center'  # h1标签居中属性
        content.insert(8, titleTag)  # 将h1标签插入整个内容的最前面

        strongTag = soup.new_tag('strong')
        strongTag['style'] = 'font-size:30px'
        strongTag.string = title  # 教程的标题
        titleTag.insert(0, strongTag)

        for i in range(4):
            brTag = soup.new_tag('br')
            content.insert(9, brTag)

    except AttributeError as er:
        pass
    finally:
        return str(content)


if __name__ == '__main__':
    articles = []
    html = 'pdfs/lxf_python3k.html'
    pdf = 'pdfs/lxf_python3k.pdf'
    if not os.path.exists('pdfs'):
        os.mkdir('pdfs')
    charpterurls = getCharpterUrl(startUrl)
    for title, url in bar(charpterurls.items()):
        articles.append(parserArticle(title, url))
        # time.sleep(1)
    # articles.append(parserArticle('title', 'https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014316090478912dab2a3a9e8f4ed49d28854b292f85bb000'))
    browser.quit()
    print('get content done, will save to local storage')

    with open(html, mode='w+', encoding='utf-8') as f:
        for article in articles:
            f.write(''.join(article))
    print('saved on local done, will covert to pdf file.')

    pdfkit.from_file(html, pdf, configuration=pdfkit_config,
                     options=pdfkit_options)

    os.remove(html)  # 对生成的临时html进行清理

    print('done')
