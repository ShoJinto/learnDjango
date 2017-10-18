#!/usr/bin/env python
#****

from urllib import request 
from bs4 import BeautifulSoup



url = r'http://www.lagou.com/zhaopin/Python/?labelWords=label'
headers = {
    'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
    'Referer': r'http://www.lagou.com/zhaopin/Python/?labelWords=label',
    'Connection':   'keep-alive'
}
req = request.Request(url,headers=headers)
page = request.urlopen(req).read()
page = page.decode('utf-8')

soup = BeautifulSoup(page,"lxml")
zhapin_info = soup.select('div.s_position_list ul.item_con_list li')

for info in zhapin_info:
#     if info['data-company'] == '畅唐网络':
        job_names = info.select('div.list_item_top div.p_top h3')
        job_publish_times = info.select('div.list_item_top div.p_top span.format-time')
        job_links = info.select('div.list_item_top div.p_top a')
        job_expers = info.select('div.list_item_top div.p_bot div.li_b_l')
        job_moneys = info.select('div.list_item_top div.p_bot div.li_b_l span.money')
        job_flags = info.select('div.list_item_bot div.li_b_l span')
        
        company_names = info.select('div.list_item_top div.company_name a')
        company_areas = info.select('div.list_item_top div.p_top span.add em')
        company_types = info.select('div.list_item_top div.industry')
        company_welfares = info.select('div.list_item_bot div.li_b_r')
        
        job_flag=[]
        for i in job_links: job_link = i['href']
        for i in job_expers: job_exper = i.contents[-1].strip()
        for i in job_flags: job_flag.append(''.join([x for x in i.stripped_strings]))
        for i in job_names: job_name = i.string
        for i in job_moneys: job_money = i.string
        for i in job_publish_times: job_publish_time = i.string
        for i in company_names: company_name = i.string
        for i in company_areas: company_area = i.string
        for i in company_types: company_type = ''.join([ x for x in i.stripped_strings])
        for i in company_welfares: company_welfare = i.string
        
#         print(job_flags,"\n", ','.join(job_flag))

        jobs = {'职位名称':job_name,'薪资':job_money,'年限及学历':job_exper, \
                '职位标签':job_flag,'公司名称':company_name,'所在地区':company_area,'公司规模':company_type, \
                '福利待遇':company_welfare,'职位链接':job_link,'发布时间':job_publish_time
                }
        
        print('=========Jobs from lagou.com=======')
        for k,v in jobs.items():
            print('%s:%s' % (k,v))
    
    
    



