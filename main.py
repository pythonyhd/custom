# -*- coding: utf-8 -*-
from scrapy import cmdline


# 天眼查-部分维度数据抓取
cmdline.execute('scrapy crawl tianyancha'.split())
# 天眼查-小程序-部分维度数据抓取(单账号抓取总数有限制)
# cmdline.execute('scrapy crawl tianyancha_applets'.split())
# 企查查-小程序-token有效时间太短-需要大量账号(爬虫意义不大)
# cmdline.execute('scrapy crawl qichacha_applets'.split())