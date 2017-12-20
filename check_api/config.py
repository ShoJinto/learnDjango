#!/usr/bin/env python
# coding:utf-8

# urls和statationUrlMapping只能任选其一
# default is False it is meaning use statationUrlMapping
useUrls = False

# 默认站点名称
station_name = "美美出行"

# api接口url对应的车站
stationUrlMapping= {
    #     "绵阳南湖":"http://2.100.100.14/czweb/StationService.asmx",
    #     "绵阳北川":"http://2.100.100.4/czweb/StationService.asmx",
    #     "绵阳富乐车站":"http://2.100.100.15/czweb/StationService.asmx",
    #     "绵阳江油":"http://2.100.100.8/czweb/StationService.asmx",
    #     "眉山洪雅":"http://2.100.100.3/czweb/StationService.asmx",
    #     "眉山中心站":"http://2.100.100.2/czweb/StationService.asmx",
    #     "遂宁城南":"http://2.100.100.11/czweb/StationService.asmx",
    #     "遂宁城北":"http://2.100.100.12/czweb/StationService.asmx",
    #     "遂宁射洪":"http://2.100.100.9/czweb/StationService.asmx",
    #     "遂宁蓬溪":"http://2.100.100.7/czweb/StationService.asmx",
    #     "遂宁安居":"http://2.100.100.13/czweb/StationService.asmx"
    "美美出行": "http://ms.mmchuxing.com/test/conn",
    "百度": "http://www.baidu11111111.com",
    "新浪": "http://www.sina.com"
}

# 需要检查的url
# url="http://ms.mmchuxing.com/test/conn"
urls = ["http://ms.mmchuxing.com/test/connssss", ]

# redis配置，
redis_host = "localhost"
redis_port = "6379"

# 报警规则设置参数
# count 出现错误的次数，interval 错误次数在这个时间段内进行累加，参考设置的意思是：如果在300毫秒内错误次数超过3此就需要报警
count = 3
interval = 300

# 第三方SMTP服务
mail_host = "smtp.mmyueche.com"
mail_user = "itservice@mmyueche.com"
mail_pass = "XULEI520xulei"

# 发送邮件帐号设置
sender = "itservice@mmyueche.com"
receivers = ["shojinto@mmyueche.com"]

# log保存路径记得最后的斜杠！！
logpath = "/var/log/"
